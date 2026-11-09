"""Clasificador multinomial Naive Bayes diminuto; datos SINTETICOS.
No usar para decisiones operativas reales. Los scores no estan calibrados.
"""
import json
import math
import re
from functools import lru_cache
from pathlib import Path

ARTIFACT = Path(__file__).resolve().parent.parent / 'assets' / 'modelo_nb.json'

def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúñü0-9]+", text.lower())

@lru_cache(maxsize=1)
def load_model() -> dict:
    return json.loads(ARTIFACT.read_text(encoding='utf-8'))

def predict(text: str) -> dict:
    model = load_model()
    words = tokenize(text)
    vocab = model['vocab_size']
    raw = {}
    for cls, item in model['classes'].items():
        score = math.log(item['documents'] / model['total_documents'])
        denom = item['token_total'] + vocab
        for word in words:
            if word in model['vocabulary']:
                score += math.log((item['counts'].get(word, 0) + 1) / denom)
        raw[cls] = score
    winner = max(raw, key=raw.get)
    exps = {label: math.exp(v - max(raw.values())) for label,v in raw.items()}
    approx = exps[winner] / sum(exps.values())
    return {'categoria': winner, 'score_no_calibrado': round(approx,4), 'modelo': 'naive_bayes_sintetico_v1'}
