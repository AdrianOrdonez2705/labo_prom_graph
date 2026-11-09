"""Entrena un Naive Bayes multinomial didactico solo con datos sinteticos."""
from collections import Counter
from pathlib import Path
import csv, json
from app.ml import tokenize

ROOT=Path(__file__).resolve().parent.parent
rows=list(csv.DictReader((ROOT/'assets'/'tickets_sinteticos.csv').open(encoding='utf-8')))
labels=sorted(set(r['categoria'] for r in rows))
vocab=set()
classes={}
for label in labels:
    texts=[r['texto'] for r in rows if r['categoria']==label]
    count=Counter(w for text in texts for w in tokenize(text))
    vocab.update(count)
    classes[label]={'documents':len(texts),'token_total':sum(count.values()),'counts':dict(sorted(count.items()))}
model={'modelo':'naive_bayes_multinomial','dataset':'tickets_sinteticos.csv','total_documents':len(rows),'vocab_size':len(vocab),'vocabulary':sorted(vocab),'classes':classes,'advertencia':'Demostrativo; scores no calibrados; no desplegar para uso real.'}
(ROOT/'assets'/'modelo_nb.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Modelo actualizado:',len(rows),'registros,',len(vocab),'tokens unicos')
