#######################################################################
# поиск по полному вхождению строки
#pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
#pylint: disable= line-too-long, redefined-outer-name

import json
import re
import os
import difflib

OUTPUT_FOLDER = "./output/"
DICTIONARIES = "./dictionaries/confiditional/"
OUTPUT_FILE = "./check_confiditinals_result.txt"

MATCH_COUNT = 0

# Функция для записи результата в файл
def write_result(file_name, content):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as output:
        output.write(f"Найдено совпадение в файле {file_name}:\n")
        output.write(f"{content}\n\n")
        output.write("\n" * 3)

# Проверка запрещенных слов и регулярных выражений
with open(OUTPUT_FILE, "w", encoding="utf-8") as output:
    output.write("Результаты проверки запрещенных слов и регулярных выражений:\n\n")

# Перебираем все файлы в папке "./output/"
for root, dirs, files in os.walk(OUTPUT_FOLDER):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Булевые флаги для каждого типа обработки
        json_match = False
        txt_without_nda_match = False
        txt_with_nda_match = False

        # Проверяем каждый файл json и txt в папке "./check_confiditinals/"
        for file_name in os.listdir(DICTIONARIES):
            if file_name.endswith(".json"):
                file_path = os.path.join(DICTIONARIES, file_name)
                with open(file_path, "r", encoding="utf-8") as check_file:
                    bad_words = json.load(check_file)
                for word, description in bad_words.items():
                    pattern = re.compile(word)
                    matches = re.findall(pattern, content)
                    if matches:
                        for match in matches:
                            MATCH_COUNT += 1
                            content = content.replace(match, description)
                            json_match = True
            elif file_name.endswith(".txt"):
                file_path = os.path.join(DICTIONARIES, file_name)
                with open(file_path, "r", encoding="utf-8") as check_file:
                    lines = check_file.readlines()
                for line in lines:
                    if line.strip() in content:
                        MATCH_COUNT += 1
                        if file_name == "clients_without_nda.txt":
                            content = content.replace(line.strip(), "[---clients_without_nda]")
                            txt_without_nda_match = True
                        elif file_name == "clients_with_nda.txt":
                            content = content.replace(line.strip(), "[---clients_with_nda]")
                            txt_with_nda_match = True

        # Записываем результат только если есть соответствующие совпадения
        if json_match or txt_without_nda_match or txt_with_nda_match:
            write_result(file, content)

# Выводим общее количество найденных совпадений
with open(OUTPUT_FILE, "a", encoding="utf-8") as output:
    output.write(f"Найдено {MATCH_COUNT} совпадений\n")

print("Проверка завершена. Результаты записаны в файл check_confiditinals_result.txt")

#######################################################################
# поиск по морфологии

# import json
# import re
# import os
# import difflib
# from pymorphy3 import MorphAnalyzer

# OUTPUT_FOLDER = "./output/"
# DICTIONARIES = "./dictionaries/confiditional/"
# OUTPUT_FILE = "./check_confiditinals_result.txt"

# match_count = 0
# count = 0

# morph = MorphAnalyzer()

# # Функция для записи результата в файл
# def write_result(file_name, content):
#     with open(OUTPUT_FILE, "a", encoding="utf-8") as output:
#         output.write(f"Найдено совпадение в файле {file_name}:\n")
#         output.write(f"{content}\n\n")
#         output.write("\n" * 3)

# # Проверка запрещенных слов и регулярных выражений
# with open(OUTPUT_FILE, "w", encoding="utf-8") as output:
#     output.write("Результаты проверки запрещенных слов и регулярных выражений:\n\n")

# # Перебираем все файлы в папке "./output/"
# for root, dirs, files in os.walk(OUTPUT_FOLDER):
#     for file in files:
#         file_path = os.path.join(root, file)
#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()
        
#         # Булевые флаги для каждого типа обработки
#         json_match = False
#         txt_without_nda_match = False
#         txt_with_nda_match = False

#         # Проверяем каждый файл json и txt в папке "./check_confiditinals/"
#         for file_name in os.listdir(DICTIONARIES):
#             if file_name.endswith(".json"):
#                 file_path = os.path.join(DICTIONARIES, file_name)
#                 with open(file_path, "r", encoding="utf-8") as check_file:
#                     bad_words = json.load(check_file)
#                 for word, description in bad_words.items():
#                     # Используем метод parse для морфологического анализа слова из словаря
#                     parsed_word = morph.parse(word)[0]
#                     pattern = re.compile(parsed_word.normal_form)  # Проверяем по нормальной форме слова
#                     matches = re.findall(pattern, content)
#                     if matches:
#                         for match in matches:
#                             match_count += 1
#                             content = content.replace(match, description)
#                             json_match = True
#             elif file_name.endswith(".txt"):
#                 file_path = os.path.join(DICTIONARIES, file_name)
#                 with open(file_path, "r", encoding="utf-8") as check_file:
#                     lines = check_file.readlines()
#                 for line in lines:
#                     parsed_line = morph.parse(line.strip())[0]  # Морфологический анализ строки из словаря
#                     parsed_content = [morph.parse(word)[0] for word in content.split()]  # Морфологический анализ контента
#                     if parsed_line in parsed_content:
#                         match_count += 1
#                         if file_name == "clients_without_nda.txt":
#                             content = content.replace(line.strip(), "[clients_without_nda]")
#                             txt_without_nda_match = True
#                         elif file_name == "clients_with_nda.txt":
#                             content = content.replace(line.strip(), "[clients_with_nda]")
#                             txt_with_nda_match = True
#             count += 1
#         # Записываем результат только если есть соответствующие совпадения
#         if json_match or txt_without_nda_match or txt_with_nda_match:
#             write_result(file, content)

# # Выводим общее количество найденных совпадений
# with open(OUTPUT_FILE, "a", encoding="utf-8") as output:
#     output.write(f"Найдено {match_count} совпадений\n")

# print("Проверка завершена. Результаты записаны в файл check_confiditinals_result.txt")