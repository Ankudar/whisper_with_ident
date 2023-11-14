#pylint: disable= missing-module-docstring, missing-function-docstring, missing-final-newline
#pylint: disable= line-too-long, redefined-outer-name
import torch
import re
from transformers import T5Tokenizer, MT5ForConditionalGeneration

def initialize_model(model_path):
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = T5Tokenizer.from_pretrained(model_path)
        model = MT5ForConditionalGeneration.from_pretrained(model_path).to(device)
        return tokenizer, model, device

    except Exception as e:
        print(f"Ошибка инициации моделей summary: {e}")
        return None, None, None

def process_files(output_file):
    try:
        model_folder = "mt5-large"
        tokenizer, model, device = initialize_model(f"./models/google/{model_folder}/")
        if tokenizer is None or model is None or device is None:
            print("Ошибка при загрузке модели, обработка файла пропущена.")
            return

        with open(output_file, 'r', encoding='utf-8') as file:
            default_text = file.read()
            text = re.sub(r'\[.*?\]', '', default_text) # удаляем все в квадратных скобках
            # print(text + "\n\n")

        task_specific_params = model.config.task_specific_params
        prefix = task_specific_params["summarization"]["prefix"] if task_specific_params is not None else ""
        inputs = tokenizer.encode(prefix + text, return_tensors='pt').to(device)

        summary_ids = model.generate(inputs, max_length=200, min_length=100, length_penalty=1, num_beams=2, repetition_penalty=1, do_sample=False)
        summary = tokenizer.decode(summary_ids[0])
        # print(summary + "\n\n")
        summary = re.sub(r'<.*?>|\.|\,', '', summary)
        # print(summary + "\n\n")

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(summary + "\n\n" + default_text)

    except Exception as e:
        print(f"Ошибка при обработке summary: {e}")
