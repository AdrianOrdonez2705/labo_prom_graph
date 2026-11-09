"""Genera trafico sintetico; ejecutable dentro de contenedor existente."""
import argparse, json, os, time, urllib.request, urllib.error
parser=argparse.ArgumentParser()
parser.add_argument('--count',type=int,default=60)
parser.add_argument('--delay',type=float,default=.12)
args=parser.parse_args()
url=os.getenv('TARGET_URL','http://api:8000').rstrip('/')+'/predict'
sentences=['servidor no responde urgente','necesito el manual actualizado','base de datos sin acceso','solicitar nuevo campo en formulario']
counts={}
for idx in range(args.count):
    payload=json.dumps({'texto':sentences[idx%len(sentences)]}).encode('utf-8')
    req=urllib.request.Request(url, payload, {'Content-Type':'application/json','X-Request-ID':f'tsi-lab-{idx:04d}'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=10) as resp:
            status=resp.status
    except urllib.error.HTTPError as err:
        status=err.code
    except Exception as ex:
        print('Fallo de conexion:',type(ex).__name__,str(ex));status='network_error'
    counts[str(status)]=counts.get(str(status),0)+1
    if (idx+1)%10==0: print(f'Progreso {idx+1}/{args.count} estados={counts}',flush=True)
    time.sleep(args.delay)
print('FIN trafico:',counts,flush=True)
