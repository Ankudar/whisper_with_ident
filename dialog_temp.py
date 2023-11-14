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