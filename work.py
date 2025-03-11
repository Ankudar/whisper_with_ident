#pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
#pylint: disable= line-too-long, redefined-outer-name
import re
import os
import time
import datetime
import sys
import warnings
import tensorflow as tf
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel, BatchedInferencePipeline
from pydub import AudioSegment
from moviepy.editor import VideoFileClip


import prepare_dialog_with_llama2

import mimetypes
import traceback
import logging

warnings.filterwarnings("ignore")
sys.stderr = open('nul', 'w')

MODEL_NAME = "large-v3"
INPUT_FOLDER = "D:/python/voice_to_text/whisper/input/"
OUTPUT_FOLDER = "D:/python/voice_to_text/whisper/output/"
CHECK_FILE = "D:/python/voice_to_text/whisper/check.txt"
NUM_THREADS = 1

FOLDERS = ["0", "key", "no_matter"]

try:
    print("Запуск модели...")
    #faster-whisper
    model = WhisperModel(MODEL_NAME, device="cuda", compute_type="float16")

    #Batched faster-whisper
    batched_model = BatchedInferencePipeline(model=model)

    print(f"Модель {MODEL_NAME} запущена")
except Exception as e:
    # root_logger.error("Произошла ошибка при загрузке модели: %s", e, exc_info=True)
    print(f"Произошла ошибка при загрузке модели: {e}")

# spkr_id_file = '.\\speaker_id.scp'
# model_random_audio = tf.keras.models.load_model("final-model")
SAMPLING_RATE = 16000

# spkr_id = {}

# with open(spkr_id_file, "r", encoding = 'utf-8') as file:
#     for line in file:
#         key, value = line.strip().split(":", 1)
#         spkr_id[int(key)] = value

def get_files():
    try:
        for folder in FOLDERS:
            path = os.path.join(INPUT_FOLDER, folder)
            files = os.listdir(path)
            if len(files) > 0:
                return path, [os.path.join(path, f) for f in files]
        return None, []
    except Exception as e:
        print(f"Ошибка при получении списка файлов: {e}")

def get_output_folder(folder_name):
    try:
        now = datetime.datetime.now()
        year = str(now.year)
        month = now.strftime("%m")
        day = now.strftime("%d")

        folder_path = os.path.join(OUTPUT_FOLDER, folder_name, year, month, day)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    except Exception as e:
        print(f"Ошибка при создании выходной папки: {e}")

def ensure_mp3(input_file):
    try:
        filename, extension = os.path.splitext(input_file)
        if extension.lower() != ".mp3":
            if extension.lower() in [".wav", ".flv", ".flac", ".ogg", ".m4a"]:
                audio = AudioSegment.from_file(input_file)
                mp3_filename = filename + ".mp3"
                audio.export(mp3_filename, format="mp3")
                os.remove(input_file)
                return mp3_filename
            elif extension.lower() in [".mp4", ".mkv", ".flv", ".avi"]:
                video = VideoFileClip(input_file)
                audio = video.audio
                mp3_filename = filename + ".mp3"
                audio.write_audiofile(mp3_filename)
                video.close()  # Закрываем объект VideoFileClip
                os.remove(input_file)
                return mp3_filename
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {extension}")
        else:
            return input_file
    except Exception as e:
        print(f"Ошибка при обработке файла {input_file}: {e}")

def delete_duplicate_lines(output_file):
    try:
        if not os.path.exists(output_file):
            return

        with open(output_file, 'r', encoding="UTF-8") as f:
            lines = f.readlines()

        new_lines = []
        seen = set()
        for line in lines:
            match = re.search(r'\[(.*?)\](.*)', line)
            if match:
                content = match.group(2).strip()
                if content not in seen:
                    seen.add(content)
                    new_lines.append(line)

        with open(output_file, 'w', encoding="UTF-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"Ошибка при удалении дубликатов из файла {output_file}: {e}")

def seconds_to_hms(seconds):
    try:
        hours, remainder = divmod(seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(remainder))
    except Exception as e:
        return None

def process_file(input_file, input_folder, output_folder):
    try:
        with open(CHECK_FILE, 'w') as f:
            f.write(input_file)
        print(f"───┐ {input_file}")

        start_time = datetime.datetime.now()
        current_time = start_time.strftime("%d-%m-%Y %H:%M:%S")
        print(f"   |─── время старта {current_time}")

        input_file = ensure_mp3(input_file)

        output_file = os.path.join(output_folder, os.path.basename(input_file) + ".txt")

        folder_name = os.path.basename(os.path.dirname(input_file))
        if folder_name in ["0", "key"]:
            segments, info = model.transcribe(input_file, beam_size=5, vad_filter=True, vad_parameters={"min_silence_duration_ms": 1500}, word_timestamps=True)
        elif folder_name == "no_matter":
            segments, info = batched_model.transcribe(input_file, batch_size=16, beam_size=5, word_timestamps=True)
        else:
            raise ValueError(f"Неподдерживаемая папка: {folder_name}")

        results = []
        for segment in segments:
            segment_start_time  = seconds_to_hms(segment.start)
            segment_end_time = seconds_to_hms(segment.end)
            results.append(f"[{segment_start_time} -> {segment_end_time}] {segment.text}\n")

        if results:
            with open(output_file, "a", encoding="UTF-8") as f:
                f.writelines(results)

            delete_duplicate_lines(output_file)

            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) < 4:
                os.remove(output_file)

        time.sleep(0.5)
        os.remove(input_file)

        segments = None
        input_file = None

        if os.path.isfile(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) >= 10:
                prepare_dialog_with_llama2.generate_summary(output_file)

        end_time = datetime.datetime.now()
        current_time = end_time.strftime("%d-%m-%Y %H:%M:%S")
        print(f"   |─── время завершения {current_time}")
        execution_time = end_time - start_time
        hours, remainder = divmod(execution_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"   |─── время обработки {hours:02}:{minutes:02}:{seconds:02}")
        print(f"   └─── осталось обработать {len(os.listdir(input_folder))}\n")
    except Exception as e:
        if "stack expects a non-empty TensorList" in str(e):
            os.remove(input_file)
        elif "list index out of range" in str(e):
            os.remove(input_file)
        else:
            print(f"Ошибка при обработке файла {input_file}: {e}")

def process():
    try:
        if os.path.exists(CHECK_FILE):
            with open(CHECK_FILE, 'r') as file:
                first_line = file.readline().strip()  # Read the first line and remove leading/trailing spaces
            if os.path.exists(first_line):
                os.remove(first_line)
    except Exception as e:
        print(f"Произошла ошибка при обработке CHECK_FILE: {e}")
        traceback.print_exc()

    no_files_flag = False

    while True:
        try:
            input_folder, files = get_files()

            if files:
                no_files_flag = False

            while len(files) > 0:
                if len(files) >= 3:
                    files_to_process = files[:3]
                    files = files[3:]
                elif files:
                    files_to_process = files[:1]
                    files = files[1:]
                else:
                    break

                if files_to_process:
                    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                        folder_names = [os.path.basename(os.path.dirname(file)) for file in files_to_process]
                        output_folder_paths = [get_output_folder(name) for name in folder_names]
                        executor.map(process_file, files_to_process, [input_folder]*len(files_to_process), output_folder_paths)

                input_folder, files = get_files()

            if not files and not no_files_flag:
                print("Нет файлов для обработки, ожидаю загрузку новых файлов")
                no_files_flag = True

            time.sleep(60)

        except Exception as e:
            print(f"Произошла ошибка в функции process(): {e}")
            traceback.print_exc()
            continue

if __name__ == '__main__':
    process()