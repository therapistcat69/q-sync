from fastapi.testclient import TestClient
from app.main import app
from app.database import initialize

client=TestClient(app)
def test_health(): assert client.get('/api/v1/health').json()['status']=='ok'
def test_ingest_and_fetch():
    initialize()
    item={"mode":"simulated","timestamp_utc":"2026-10-28T10:00:00Z","digital":{"timestamp_utc":"2026-10-28T10:00:00Z","sampling_interval_ms":1000,"cpu":{"usage_percent":21},"memory":{"usage_percent":45},"disk_io":{}},"physical":{"timestamp_utc":"2026-10-28T10:00:00Z","temperature":{"object_temperature_c":30},"motion":{"acceleration_g":{"x":0,"y":0,"z":1},"acceleration_magnitude_g":1}}}
    assert client.post('/api/v1/telemetry',json=item).status_code==201
    assert client.get('/api/v1/telemetry/current').status_code==200
