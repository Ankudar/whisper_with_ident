import os
from pathlib import Path
from shutil import copy2
from tqdm import tqdm
import time
import datetime

# Исходная и конечная директории
src_dir = r'C:/Users/root6/Desktop/python/'
dst_dir = r'//192.168.5.212/E$/python/bac_from_ib-rtx/'

# Список папок для исключения содержимого
exclude_dirs = ['zoom_api/zoom_recording', 'LLAMA', 
                'machine_learning/train/data_set', 'machine_learning/train/обработка аудио_СКОПИРОВАТЬ_НЕ_ИСПОЛЬЗОВАТЬ_НАПРЯМУЮ', 
                'voice_to_text/whisper/input', 'voice_to_text/whisper/models']

def copy_files(src_path, dst_path):
    if not dst_path.exists():
        dst_path.mkdir(parents=True)

    for child in src_path.iterdir():
        if child.is_dir():
            if child.name not in exclude_dirs:
                copy_files(child, dst_path / child.name)
        else:
            if src_path.name not in exclude_dirs:
                copy2(child, dst_path / child.name)
                pbar.update(1)

def get_all_files(path):
    files = []
    for item in path.iterdir():
        if item.is_dir():
            if item.name not in exclude_dirs:
                files += get_all_files(item)
        elif item.is_file():
            files.append(item)
    return files

files_to_copy = get_all_files(Path(src_dir))

pbar = tqdm(total=len(files_to_copy), ncols=100)
while True:
    # Создание подпапок с текущей датой
    current_date = time.strftime('%Y/%m/%d')
    dst_dir_new = Path(dst_dir) / current_date

    # Проверка, производилось ли копирование сегодня
    if not dst_dir_new.exists():
        copy_files(Path(src_dir), dst_dir_new)

    # Проверка времени и ожидание следующего дня для повторного копирования
    current_time = datetime.datetime.now()
    next_day = (current_time + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0)
    time_to_next_day = (next_day - current_time).total_seconds()
    time.sleep(time_to_next_day)

pbar.close()