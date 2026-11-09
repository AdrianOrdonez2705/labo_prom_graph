"""Prueba HTTP local que solo requiere Python ya dentro del contenedor."""
import json, urllib.request
root='http://api:8000'
for path in ('/health','/metrics'):
    with urllib.request.urlopen(root+path,timeout=5) as resp:
        print(path,resp.status)
req=urllib.request.Request(root+'/predict', data=json.dumps({'texto':'servidor no responde urgente'}).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(req,timeout=5) as resp:
    print('/predict',resp.status,resp.read().decode()[:200])
