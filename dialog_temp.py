#pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
#pylint: disable= line-too-long, redefined-outer-name
# import os
# from dostoevsky.tokenization import RegexTokenizer
# from dostoevsky.models import FastTextSocialNetworkModel

# tokenizer = RegexTokenizer()

# # Получаем список файлов и директорий в папке './dialog_test/'
# file_dir = './dialog_test/'
# messages = []
# filenames = []

# # Рекурсивная функция для обхода директории
# def process_directory(directory):
#     for item in os.listdir(directory):
#         item_path = os.path.join(directory, item)
#         if os.path.isfile(item_path):
#             with open(item_path, 'r', encoding='utf-8') as file:
#                 # Добавляем содержимое файла в список сообщений
#                 messages.append(file.read())
#                 # Добавляем путь к файлу в список имен
#                 filenames.append(item_path)
#         elif os.path.isdir(item_path):
#             # Рекурсивно вызываем функцию для вложенной директории
#             process_directory(item_path)

# # Обрабатываем директорию "dialog_test" с помощью рекурсивной функции
# process_directory(file_dir)

# model = FastTextSocialNetworkModel(tokenizer=tokenizer)

# results = model.predict(messages, k=2)

# # Выводим результаты предсказаний для каждого файла
# for filename, sentiment in zip(filenames, results):
#     first_word = list(sentiment.keys())[0]
#     with open(filename, 'a', encoding='utf-8') as file:
#         file.write("\n\nТональность беседы - " + first_word)

####################################################################
# основной рабочий вариант
# import os
# from dostoevsky.tokenization import RegexTokenizer
# from dostoevsky.models import FastTextSocialNetworkModel

# tokenizer = RegexTokenizer()

# def process_file(output_file):
#     try:
#         messages = []
#         filenames = []

#         with open(output_file, 'r', encoding='utf-8') as file:
#             messages.append(file.read())
#             filenames.append(output_file)

#         model = FastTextSocialNetworkModel(tokenizer=tokenizer)

#         results = model.predict(messages, k=2)

#         first_word = list(results[0].keys())[0]
#         with open(output_file, 'a', encoding='utf-8') as file:
#             file.write("\n\nТональность беседы - " + first_word + "\n")

#     except Exception:
#         pass


###################################################################
# тестирование с разбивкой текста на части и вычисление средней тональности по всем предложениям

import os
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from nltk.tokenize import sent_tokenize

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

sentiment_values = {
  'superpositive': 1,
  'neutral': 0,
  'supernegative': -1
}

def process_file(output_file):
    try:
        with open(output_file, 'r', encoding='utf-8') as file:
            text = file.read()
        sentences = sent_tokenize(text)
        results = [model.predict([sent], k=2) for sent in sentences]

        sentiments = [sentiment_values[list(res[0].keys())[0]] for res in results]
        avg_sentiment = sum(sentiments) / len(sentiments)

    except Exception:
        avg_sentiment = 0 # здесь мы делаем его нейтральным в случае исключения

    sentiment_str = 'neutral'
    if avg_sentiment <= -0.7:
        sentiment_str = 'supernegative'
    elif -0.7 < avg_sentiment <= -0.01:
        sentiment_str = 'negative'
    elif 0.01 < avg_sentiment <= 0.69:
        sentiment_str = 'positive'
    elif avg_sentiment >= 0.7:
        sentiment_str = 'superpositive'

    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(f"\n\nТональность беседы - {sentiment_str} ({avg_sentiment})\n")