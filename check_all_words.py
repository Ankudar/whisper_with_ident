# #pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
# #pylint: disable= line-too-long, redefined-outer-name
import os
import re
import string
from collections import Counter

OUTPUT_FOLDER = "./output/"

def remove_punctuation_and_brackets(input_string):
    # Удаляем квадратные скобки и содержимое внутри них
    input_string = re.sub(r'"\[.*?\]"', ' ', input_string)
    # Удаляем знаки препинания
    for c in string.punctuation:
        input_string = input_string.replace(c, "")
    # Удаляем цифры
    input_string = re.sub(r'd', ' ', input_string)
    # Удаляем слова, которые заканчиваются на 's' и предшествованы числами
    input_string = re.sub(r'bd+sb', ' ', input_string)
    return input_string

word_count = Counter()
total_files = sum([len(files) for r, d, files in os.walk(OUTPUT_FOLDER) if any(fname.endswith('.txt') for fname in files)])

print(f"Всего файлов для обработки: {total_files}")

file_count = 0

for root, dirs, files in os.walk(OUTPUT_FOLDER):
    for file in files:
        if file.endswith(".txt"):
            file_count += 1
            print(f"Обрабатывается файл {file_count} из {total_files}")
            with open(os.path.join(root, file), "r", encoding='utf-8') as f:
                for line in f:
                    line = remove_punctuation_and_brackets(line)
                    words = [word for word in line.lower().split() if len(word) > 3]  # оставляем только слова, которые более чем на 3 символа
                    word_count.update(words)

if word_count:
    word_count = sorted(word_count.items(), key=lambda item: item[1], reverse=True)  # сортировка по убыванию частоты
    with open("word_count.txt", "w", encoding='utf-8') as f:
        for word, count in word_count:
            f.write(f"{word}: {count}\n")
else:
    print("Не найдено ни одного слова для обработки.")