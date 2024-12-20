import os
import wave
import tensorflow as tf
import librosa
import re
import numpy as np 
from collections import Counter
from pydub import AudioSegment
import io

def prepare_for_ident(input_file, SAMPLING_RATE):
    target_dBFS = -30.0
    try:
        if not input_file.endswith('.wav'):
            audio = AudioSegment.from_file(input_file)
            wav_path = os.path.splitext(input_file)[0] + '.wav'
            audio.export(wav_path, format='wav')
            os.remove(input_file)

            with wave.open(wav_path, 'rb') as wave_file:
                current_sample_rate = wave_file.getframerate()

            if current_sample_rate != SAMPLING_RATE:
                audio = AudioSegment.from_wav(wav_path)
                resampled_audio = audio.set_frame_rate(SAMPLING_RATE)
                resampled_audio.export(wav_path, format='wav')
            input_file = wav_path

        # Convert stereo to mono
        sound = AudioSegment.from_wav(input_file)
        if sound.channels > 1:
            sound = sound.set_channels(1)
            sound.export(input_file, format="wav")

        # Match amplitude
        if input_file.endswith('.wav'):
            audio = AudioSegment.from_file(input_file)
            normalized_audio = audio.apply_gain(target_dBFS - audio.dBFS)
            normalized_audio.export(input_file, format='wav')

        return input_file
    except Exception as e:
        print(f"Error in prepare_for_ident function: {e}")

def data_gen(wav):
    try:
        wav_parts = [wav[i:i+32000] for i in range(0, len(wav), 32000) if len(wav[i:i+32000]) == 32000]
        wav_arrs = [np.array([part.tolist()]) for part in wav_parts]
        return wav_arrs
    except Exception as e:
        print(f"Error in data_gen function: {e}")

def extract_timing(output_file):
    try:
        with open(output_file, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            timings = [re.findall(r'\[(.*?)s -> (.*?)s\]', line) for line in lines]
            return [(float(start), float(end)) for timing in timings for start, end in timing]
    except Exception as e:
        print(f"Error in extract_timing function: {e}")

def convert_seconds_to_ms(timings):
    try:
        return [(start * 1000, end * 1000) for start, end in timings]
    except Exception as e:
        print(f"Error in convert_seconds_to_ms function: {e}")

def extract_based_on_timing(timings, audio_segment):
    try:
        return [audio_segment[start:end] for start, end in convert_seconds_to_ms(timings)]
    except Exception as e:
        print(f"Error in extract_based_on_timing function: {e}")

def replace_timing_with_speaker(output_file, timings, speakers):
    try:
        with open(output_file, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        for i, (speaker, prob) in enumerate(speakers):
            timing_line = f"[{timings[i][0]}s -> {timings[i][1]}s]"
            for j in range(len(lines)):
                if timing_line in lines[j]:
                    lines[j] = lines[j].replace(timing_line, f"{timing_line} {{{speaker}, {prob:.2f}%}}")
        with open(output_file, 'w', encoding="utf-8") as f:
            f.writelines(lines)
    except Exception as e:
        print(f"Error in replace_timing_with_speaker function: {e}")

def run_ident(input_file, output_file, spkr_id, model_random_audio, SAMPLING_RATE):
    if not os.path.exists(output_file):
        os.remove(input_file)
        return
    try:
        input_file = prepare_for_ident(input_file, SAMPLING_RATE)
        audio = AudioSegment.from_file(input_file)
        timings = extract_timing(output_file)
        fragments = extract_based_on_timing(timings, audio)

        spkrs = []
        for fragment in fragments:
            if len(fragment) > 2 * SAMPLING_RATE:
                chunks = [fragment[i:i + 2 * SAMPLING_RATE] for i in range(0, len(fragment), 2 * SAMPLING_RATE)]
                chunks = chunks[:-1]  # отбрасываем последний фрагмент
            elif len(fragment) < 2 * SAMPLING_RATE:
                silence = AudioSegment.silent(duration=(2 * SAMPLING_RATE - len(fragment)))
                fragment = fragment + silence
                chunks = [fragment]
            else:
                chunks = [fragment]

            for chunk in chunks:
                # Use BytesIO instead of a temporary file
                byte_stream = io.BytesIO()
                chunk.export(byte_stream, format="wav")
                byte_stream.seek(0)  # Reset the stream position to the beginning
                wav,_ = librosa.load(byte_stream, sr=SAMPLING_RATE)
                new_file_arrs = data_gen(wav)
                for arr in new_file_arrs:
                    pred_spk = model_random_audio.predict(arr, verbose=0)
                    spkr = np.argmax(pred_spk)
                    probability = np.max(pred_spk) * 100
                    if probability >= 95:
                        spkrs.append((spkr_id[spkr], probability))
                        # print(f"{spkr_id[spkr]} ---- {probability}")

        if spkrs:
            most_common_spkr = Counter([spkr for spkr, _ in spkrs]).most_common(1)[0]
            replace_timing_with_speaker(output_file, timings, spkrs)
        os.remove(input_file)
    except Exception as e:
        print(f"Ошибка в функции run_ident: {e}")

def set_speaker(input_file, output_file, spkr_id, model_random_audio, SAMPLING_RATE):
    run_ident(input_file, output_file, spkr_id, model_random_audio, SAMPLING_RATE)
