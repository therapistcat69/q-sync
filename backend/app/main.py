from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import json
from uuid import uuid4
from .config import API_PREFIX, FRONTEND_ORIGINS, FRONTEND_DIST
from .database import initialize, connect
from .models import ObservationIn, ExperimentIn, IncidentUpdate
from .services import store_observation, simulate

app=FastAPI(title="Q-SYNC API",version="0.1.0",openapi_url=f"{API_PREFIX}/openapi.json")
app.add_middleware(CORSMiddleware,allow_origins=FRONTEND_ORIGINS,allow_methods=["GET","POST","PATCH"],allow_headers=["Content-Type"],allow_credentials=False)
clients=[]
@app.on_event("startup")
def startup(): initialize()
async def broadcast(event):
    for client in clients.copy():
        try: await client.send_json(event)
        except Exception: clients.remove(client)
@app.get(f"{API_PREFIX}/health")
def get_health(): return {"status":"ok","database":"ok","version":"0.1.0"}
@app.post(f"{API_PREFIX}/telemetry",status_code=201)
async def ingest(payload: ObservationIn):
    result=store_observation(payload.model_dump(mode="json")); await broadcast({"type":"observation","data":result}); return result
@app.get(f"{API_PREFIX}/telemetry/current")
def current():
    with connect() as db: row=db.execute("SELECT payload,assessment,created_at FROM observations ORDER BY timestamp_utc DESC LIMIT 1").fetchone()
    if not row: raise HTTPException(404,"No telemetry has been received")
    return {**json.loads(row["payload"]),"assessment":json.loads(row["assessment"]),"created_at":row["created_at"]}
@app.get(f"{API_PREFIX}/telemetry/history")
def history(limit:int=100):
    with connect() as db: rows=db.execute("SELECT payload,assessment,created_at FROM observations ORDER BY timestamp_utc DESC LIMIT ?",(min(max(limit,1),500),)).fetchall()
    return [{**json.loads(r["payload"]),"assessment":json.loads(r["assessment"]),"created_at":r["created_at"]} for r in rows]
@app.get(f"{API_PREFIX}/incidents")
def incidents():
    with connect() as db: rows=db.execute("SELECT * FROM incidents ORDER BY created_at DESC").fetchall()
    return [{**dict(r),"evidence":json.loads(r["evidence"])} for r in rows]
@app.patch(f"{API_PREFIX}/incidents/{{incident_id}}")
def update_incident(incident_id:str, update:IncidentUpdate):
    with connect() as db:
        if not db.execute("SELECT 1 FROM incidents WHERE id=?",(incident_id,)).fetchone(): raise HTTPException(404,"Incident not found")
        db.execute("UPDATE incidents SET status=? WHERE id=?",(update.status,incident_id))
    return {"id":incident_id,"status":update.status}
@app.post(f"{API_PREFIX}/experiments",status_code=201)
async def experiment(request:ExperimentIn):
    eid=f"exp-{uuid4().hex[:10]}"; result=simulate(request.scenario)
    with connect() as db: db.execute("INSERT INTO experiments VALUES (?, ?, 'complete', ?, ?)",(eid,request.scenario,json.dumps(result),datetime.utcnow().isoformat()))
    await broadcast({"type":"observation","data":result}); return {"id":eid,"scenario":request.scenario,"status":"complete","result":result}
@app.get(f"{API_PREFIX}/research/metrics")
def metrics(): return {"status":"insufficient_data","message":"Metrics require labelled stored experiments; no fabricated confusion matrix is returned.","precision":None,"recall":None,"f1":None,"false_alarm_rate":None,"latency_ms":None}
@app.get(f"{API_PREFIX}/reports/summary")
def report():
    with connect() as db: count=db.execute("SELECT count(*) c FROM observations").fetchone()["c"]; incidents=db.execute("SELECT count(*) c FROM incidents WHERE status != 'resolved'").fetchone()["c"]
    return {"generated_at":datetime.utcnow().isoformat()+"Z","observation_count":count,"open_incidents":incidents,"limitations":["ML and quantum engines are not integrated in this local baseline.","Report is derived from locally stored observations."]}
@app.websocket(f"{API_PREFIX}/stream")
async def stream(websocket:WebSocket):
    await websocket.accept(); clients.append(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in clients: clients.remove(websocket)

# Production/local-tunnel mode: one origin serves the compiled console and API.
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")
    @app.get("/{path:path}", include_in_schema=False)
    def console(path: str):
        return FileResponse(FRONTEND_DIST / "index.html")
