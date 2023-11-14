# #pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
# #pylint: disable= line-too-long, redefined-outer-name
import re
import os
import time
import datetime
import sys
import warnings
import tensorflow as tf
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

import get_ident

import mimetypes

# import dialog_temp
# import dialog_markers
# import dialog_summary

warnings.filterwarnings("ignore")
sys.stderr = open('nul', 'w')

MODEL_NAME = "large-v2"
INPUT_FOLDER = "./input/"
OUTPUT_FOLDER = "./output/"
# NUM_THREADS = os.cpu_count() - 4  # Количество доступных процессорных ядер
NUM_THREADS = 8

FOLDERS = ["0", "key", "no_matter"]

try:
    print("Загрузка модели...")
    model = WhisperModel(MODEL_NAME, device="cuda", compute_type="float16")
    # or run on GPU with INT8
    # model = WhisperModel(MODEL_NAME, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    # model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
    print(f"Модель {MODEL_NAME} загружена")
except Exception as e:
    print(f"Произошла ошибка при загрузке модели: {e}")

spkr_id_file = './speaker_id.scp'
model_random_audio = tf.keras.models.load_model("final-model")
SAMPLING_RATE = 16000

spkr_id = {}

with open(spkr_id_file, "r", encoding = 'utf-8') as file:
    for line in file:
        key, value = line.strip().split(":", 1)
        spkr_id[int(key)] = value

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

def delete_duplicate_lines(output_file):
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

def process_file(input_file, input_folder, output_folder):
    try:
        print(f"---- {input_file}")

        start_time = datetime.datetime.now()
        current_time = start_time.strftime("%d-%m-%Y %H:%M:%S")
        print(f"   |--- время старта {current_time}")

        input_file = ensure_mp3(input_file)

        output_file = os.path.join(output_folder, os.path.basename(input_file) + ".txt")
        segments, info = model.transcribe(input_file, beam_size=5, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=1500)) #700

        results = []
        for segment in segments:
            results.append("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text) + "\n")
        # Записать результаты в файл только если список не пуст
        if results:
            with open(output_file, "a", encoding="UTF-8") as f:
                f.writelines(results)

        delete_duplicate_lines(output_file)
        # get_ident.set_speaker(input_file, output_file, spkr_id, model_random_audio, SAMPLING_RATE)

        os.remove(input_file)

        segments = None
        input_file = None

        # сюда дописать добавление в конечный файл маркеров тональности беседы, преступлений и т.д.
        # if os.path.isfile(output_file):
        #     dialog_summary.process_files(output_file)
        #     dialog_temp.process_file(output_file)
        #     dialog_markers.process_files(output_file)

        end_time = datetime.datetime.now()
        current_time = start_time.strftime("%d-%m-%Y %H:%M:%S")
        print(f"   |--- время завершения {current_time}")
        execution_time = end_time - start_time
        hours, remainder = divmod(execution_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"   |--- время обработки {hours}:{minutes}:{seconds}")
        print(f"   |--- осталось обработать {len(os.listdir(input_folder))}")
    except Exception as e:
        print(f"Ошибка при обработке файла {input_file}: {e}")

def process():
    while True:
        input_folder, files = get_files()

        if len(files) > 0:
            with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                folder_names = [os.path.basename(os.path.dirname(file)) for file in files]
                output_folder_paths = [get_output_folder(name) for name in folder_names]
                executor.map(process_file, files, [input_folder]*len(files), output_folder_paths)

                # Update files after processing a batch
                _, new_files = get_files()

                # Add new files to existing files (with higher priority)
                files = new_files + files

        else:
            print("Нет файлов для обработки, ожидаю загрузку новых файлов")
            time.sleep(60)

# Перенаправление stderr обратно на консоль
# sys.stderr = sys.__stderr__

if __name__ == '__main__':
    process()