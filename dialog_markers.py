#pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
#pylint: disable= line-too-long, redefined-outer-name
import os
import re
import pymorphy3
import nltk
from nltk.corpus import stopwords

def process_files(output_file):
    try:
        dictionaries_folder = './dictionaries/marks/'
        dictionary_files = os.listdir(dictionaries_folder)
        morph = pymorphy3.MorphAnalyzer()
        russian_stopwords = stopwords.words("russian")

        def read_dictionary(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()

        def read_input_file(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = re.sub(r'\[.*?\]', '', f.read()) # удаляем все в квадратных скобках
                words = [word for word in text.split() if word not in russian_stopwords]
                return [morph.normal_forms(word)[0] for word in words]

        def calculate_and_print_similarity(file_words, dictionary_lines, dictionary_name):
            total_words = len(file_words)
            matching_words = 0

            for word in file_words:
                for line in dictionary_lines:
                    if morph.normal_forms(word)[0] in line.split():
                        matching_words += 1

            return (matching_words / total_words) * 100

        with open(output_file, 'a', encoding='utf-8') as f:
            for dictionary_file in dictionary_files:
                dictionary_path = os.path.join(dictionaries_folder, dictionary_file)
                dictionary_name = os.path.splitext(dictionary_file)[0]

                dictionary_lines = read_dictionary(dictionary_path)
                output_file_words = read_input_file(output_file)

                similarity = calculate_and_print_similarity(output_file_words, dictionary_lines, dictionary_name)

                if str(similarity) != "0.0":
                    if similarity < 1:
                        category = "low"
                    elif similarity < 3:
                        category = "medium"
                    elif similarity > 3:
                        category = "high"

                    f.write(f"{dictionary_name} - {category}\n")
    except Exception as e:
        print(e)