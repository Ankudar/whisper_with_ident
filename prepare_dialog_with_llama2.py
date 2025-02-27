import textwrap
import os
import gc
from llama_cpp import Llama

MODEL_PATH = "D:/python/voice_to_text/whisper/models/7B/OpenHermes-2.5-neural-chat-7b-v3-1-7B-Mistral-7B-Instruct-v0.2-slerp.Q5_K_M.gguf"

N_THREADS = 15
N_BATCH = 512
N_GPU_LAYERS = 100
N_CTX = 10000 #8192
MAX_TOKENS = -1
TEMPERATURE = 0.7
TOP_P = 0.95
TOP_K = 40
REPEAT_PENALTY = 1.1

LLM = Llama(
    model_path=f"{MODEL_PATH}",
    n_threads = N_THREADS,
    n_batch = N_BATCH, # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
    n_gpu_layers = N_GPU_LAYERS,
    n_ctx = N_CTX,
    verbose=False
    )

SYSTEM_PROMPT = """Проанализируйте предоставленный диалог и дайте ответы, соответствующие следующим пунктам. Ответы должны быть предельно краткими, однословными и точно отражать суть каждого вопроса:
О чем диалог?
Каков общий тон диалога?
Обсуждается ли в диалоге увольнение и собеседования?
Есть ли в диалоге обсуждение оффера, вакансии и предложение работы?
Присутствуют ли в диалоге признаки вредительства?
Есть ли упоминания о том, что личная жизнь мешает работе?
Свидетельствует ли диалог о наличии стресса у собеседников?
Можно ли в разговоре уловить конфликты интересов?
Ваши ответы должны соответствовать формату:

[О чем диалог] - краткая выжимка беседы - как начали беседу, что обсуждали в ходе беседы, к какому решению пришли и что будут делать дальше
[Тон] - дружественный/нейтральный/негативный
[Увольнение] - да/нет
[Оффер] - да/нет
[Вредительство] - да/нет
[Личная жизнь] - да/нет
[Стресс] - да/нет
[Конфликты] - да/нет

Все ответы должны быть представлены на русском языке.
"""

def generate_summary(output_file):
    try:
        with open(output_file, 'r', encoding='utf-8') as file:
            text = file.read()

        try:
            output = LLM(
                f"{SYSTEM_PROMPT}\n\n###Instruction:\n\n{text}\n\n###Response:",
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                top_k=TOP_K,
                repeat_penalty=REPEAT_PENALTY
            )
            generated_text = output["choices"][0]["text"].strip()
        except Exception as e:
            print(f"generate_summary - Ошибка при генерации: {e}")
            generated_text = ""
        finally:
            # Очистка памяти, если LLM создает большие временные объекты
            del output
            gc.collect()

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(generated_text + '\n\n')
            file.write(text)
    except Exception as e:
        print(f"generate_summary - Ошибка при работе с файлом: {e}")
    finally:
        # Очистка памяти, если 'text' и 'generated_text' большие
        del text, generated_text
        gc.collect()
