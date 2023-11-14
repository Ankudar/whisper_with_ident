#######################################################################
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

def write_result(file_name, content):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as output:
        output.write(f"Найдено совпадение в файле {file_name}:\n")
        output.write(f"{content}\n\n")
        output.write("\n" * 3)

with open(OUTPUT_FILE, "w", encoding="utf-8") as output:
    output.write("Результаты проверки запрещенных слов и регулярных выражений:\n\n")

for root, dirs, files in os.walk(OUTPUT_FOLDER):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        json_match = False
        txt_without_nda_match = False
        txt_with_nda_match = False

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

        if json_match or txt_without_nda_match or txt_with_nda_match:
            write_result(file, content)

with open(OUTPUT_FILE, "a", encoding="utf-8") as output:
    output.write(f"Найдено {MATCH_COUNT} совпадений\n")

print("Проверка завершена. Результаты записаны в файл check_confiditinals_result.txt")