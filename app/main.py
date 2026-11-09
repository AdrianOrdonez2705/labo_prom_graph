"""API demostrativa de clasificacion de tickets, no apta para produccion."""
import asyncio
import json
import logging
import os
import re
import threading
import time
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from app.ml import predict

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger('tsi_lab')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
INCIDENT_MODE = os.getenv('INCIDENT_MODE', 'off')
REQUESTS = Counter('tsi_http_requests', 'Peticiones por codigo y ruta normalizada', ['method','path','status'])
LATENCY = Histogram('tsi_http_request_duration_seconds', 'Duracion peticiones', ['method','path'], buckets=(.01,.05,.1,.25,.5,1,2,5))
PREDICTIONS = Counter('tsi_predictions', 'Predicciones por etiqueta', ['categoria'])
_lock = threading.Lock()
_calls = 0

app = FastAPI(title='TSI EC3 - API de inferencia (datos sinteticos)', version=APP_VERSION)

class Ticket(BaseModel):
    texto: str = Field(min_length=3, max_length=500, description='Descripcion ficticia de ticket')

def log_event(**event):
    LOG.info(json.dumps(event, ensure_ascii=False, separators=(',',':')))

@app.middleware('http')
async def capture(request: Request, call_next):
    # Nunca registrar cuerpo, tokens, contrasenas ni texto del ticket.
    start = time.perf_counter()
    candidate = request.headers.get('X-Request-ID','')
    request_id = candidate if re.fullmatch(r'[A-Za-z0-9._-]{1,64}',candidate) else uuid.uuid4().hex
    request.state.request_id = request_id
    if request.url.path == '/metrics':
        return await call_next(request)
    path = request.url.path if request.url.path in ('/','/health','/predict') else '/other'
    status=500
    try:
        response=await call_next(request)
        status=response.status_code
        response.headers['X-Request-ID']=request_id
        return response
    except Exception:
        log_event(event='unhandled_exception', request_id=request_id, path=path, version=APP_VERSION)
        raise
    finally:
        elapsed=time.perf_counter()-start
        REQUESTS.labels(method=request.method,path=path,status=str(status)).inc()
        LATENCY.labels(method=request.method,path=path).observe(elapsed)
        log_event(event='http_request',request_id=request_id,method=request.method,path=path,status=status,duration_ms=round(elapsed*1000,2),version=APP_VERSION)

@app.get('/')
def index():
    return {'servicio':'tsi-ec3','version':APP_VERSION,'demo':'clasificador sintetico de tickets','endpoints':['/health','/predict','/metrics','/docs']}

@app.get('/health')
def health():
    return {'status':'ok','version':APP_VERSION,'incident_mode':INCIDENT_MODE}

@app.post('/predict')
async def infer(ticket: Ticket, request: Request):
    global _calls
    with _lock:
        _calls+=1
        order=_calls
    if INCIDENT_MODE == 'degraded':
        await asyncio.sleep(0.65)
        if order % 3 == 0:
            raise HTTPException(status_code=503, detail='Falla simulada en release 1.1.0 (solo laboratorio)')
    result=predict(ticket.texto)
    PREDICTIONS.labels(categoria=result['categoria']).inc()
    return {'request_id':request.state.request_id,'version':APP_VERSION,**result}

@app.get('/metrics')
def metrics():
    return Response(content=generate_latest(),media_type=CONTENT_TYPE_LATEST)
