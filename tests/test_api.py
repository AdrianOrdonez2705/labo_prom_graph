from fastapi.testclient import TestClient
from app.main import app
from app.ml import predict

client=TestClient(app)

def test_health():
    r=client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_inference():
    r=client.post('/predict',json={'texto':'servidor no responde urgente'})
    assert r.status_code == 200
    assert r.json()['categoria'] in ('critico','normal')
    assert 'score_no_calibrado' in r.json()
    assert r.headers.get('X-Request-ID')

def test_validation():
    assert client.post('/predict',json={'texto':'a'}).status_code == 422

def test_metrics():
    r=client.get('/metrics')
    assert r.status_code == 200
    assert 'tsi_http_requests_total' in r.text

def test_models():
    assert predict('servidor no responde urgente')['categoria']=='critico'
    assert predict('solicito el manual de usuario')['categoria']=='normal'

def test_log_no_pii(caplog):
    # El cuerpo con un texto de prueba no debe registrarse.
    marker='DOCUMENTO_SUPER_SECRETO_99999'
    with caplog.at_level('INFO'):
        client.post('/predict',json={'texto':marker})
    assert marker not in caplog.text
