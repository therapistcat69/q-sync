# Q-SYNC local prototype

Q-SYNC is a local cyber-physical telemetry console. It implements schema-validated ingestion, SQLite persistence, evidence-preserving assessment, incident records, simulations, REST/OpenAPI and WebSocket events.

## Run

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API reference is at `http://localhost:8001/docs` and is bound locally by default.

## Dev Tunnels

The frontend proxies `/api` and WebSocket connections to the local backend. For a Dev Tunnel, first build the frontend and expose **only port 8001**: FastAPI serves the built console, API, and WebSocket under one HTTPS origin. No CORS wildcard is required.

```powershell
# terminal 1
cd frontend
npm run build

# terminal 2
cd ..\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8001

# terminal 3 (sign in once, then host; Dev Tunnels requires an authenticated account)
devtunnel user login
devtunnel host -p 8001 --allow-anonymous
```

Use the HTTPS URL printed by Dev Tunnels. Keep the terminal open while sharing. To expose the API separately, set `QSYNC_FRONTEND_ORIGINS` to the exact comma-separated frontend origins; never set it to `*` for a public tunnel.

## Contracts

- `POST /api/v1/telemetry` accepts the validated subset of the supplied observation schema and persists the original payload.
- `GET /api/v1/telemetry/current`, `GET /api/v1/telemetry/history`, `GET /api/v1/incidents`
- `POST /api/v1/experiments` accepts one of `baseline`, `cpu_spike`, `thermal_rise`, `vibration`, `wifi_change`, `timing_lag`, `combined`.
- WebSocket: `ws://localhost:8000/api/v1/stream`; receive JSON `{ type: "observation", data: Observation }` events. Send any text to keep the connection alive.

SQLite initializes automatically as `backend/qsync.db`. ML and Qiskit/ProbiCore are explicit integration points: their values are reported unavailable until validated modules are connected, rather than being fabricated. Serial ingestion is intentionally not enabled: connect a host serial adapter that validates the approved record shape then posts it to the telemetry endpoint.

## Test

```powershell
cd backend
pytest -q
```
