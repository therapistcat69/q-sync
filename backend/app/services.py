from datetime import datetime, timezone
from uuid import uuid4
from .database import connect, dump
from .config import POLICY_VERSION

def now(): return datetime.now(timezone.utc).isoformat()

def assess(data: dict):
    d, p, wifi = data["digital"], data["physical"], data.get("wifi", {})
    indicators, uncertainties = [], []
    if d["cpu"]["usage_percent"] >= 90: indicators.append({"source":"digital","name":"cpu_usage_percent","value":d["cpu"]["usage_percent"],"interpretation":"Sustained high CPU warrants correlation with physical evidence."})
    temp = p["temperature"].get("object_temperature_c")
    if temp is not None and temp >= 65: indicators.append({"source":"physical","name":"object_temperature_c","value":temp,"interpretation":"Temperature is outside the configured observation range."})
    vibration = p["motion"].get("vibration_rms_g") or p["motion"].get("acceleration_magnitude_g")
    if vibration and vibration >= 2: indicators.append({"source":"physical","name":"motion_g","value":vibration,"interpretation":"Elevated motion needs investigation with device context."})
    if wifi.get("scan_status") == "ok" and wifi.get("access_point_count", 0) > 15: indicators.append({"source":"wifi","name":"access_point_count","value":wifi["access_point_count"],"interpretation":"Environmental change is contextual evidence, not proof of intrusion."})
    if wifi.get("scan_status") != "ok": uncertainties.append("Wi-Fi environment is unavailable or incomplete.")
    if not indicators: status, severity, title = "normal", None, None
    elif len(indicators) == 1: status, severity, title = "warning", "low", "Single anomalous indicator"
    else: status, severity, title = "incident", "medium", "Cross-domain inconsistency requires investigation"
    return {"status":status,"severity":severity,"title":title,"summary":"No inconsistency indicators were triggered." if not indicators else "Multiple sources should be reviewed; this is not a confirmed attack.","indicators":indicators,"evidence_refs":[],"uncertainties":uncertainties,"policy_version":POLICY_VERSION}

def health(data):
    return {"serial_connection":"unknown" if data["mode"] == "live" else "simulated","esp32":"unknown" if data["mode"] == "live" else "simulated","host_collector":"ok","feature_engine":"ok","ml_engine":"unavailable","quantum_engine":"unavailable","database":"ok","websocket":"ok"}

def store_observation(data):
    oid = data.get("observation_id") or f"obs-{uuid4().hex[:12]}"; data["observation_id"] = oid
    assessment = assess(data); created = now()
    with connect() as db:
        db.execute("INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)",(oid, data["timestamp_utc"],data["mode"],dump(data),dump(assessment),created))
        if assessment["status"] == "incident":
            iid=f"inc-{uuid4().hex[:10]}"; db.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?)",(iid,oid,"open",assessment["severity"],assessment["title"],dump(assessment),created)); assessment["event_id"]=iid
    return {**data,"assessment":assessment,"health":health(data),"created_at":created}

def simulate(scenario):
    base={"mode":"simulated","timestamp_utc":now(),"metadata":{"device_id":"simulator","host_id":"qsync-local"},"digital":{"timestamp_utc":now(),"sampling_interval_ms":1000,"cpu":{"usage_percent":28},"memory":{"usage_percent":55},"disk_io":{"read_bytes_per_sec":1000,"write_bytes_per_sec":500}},"physical":{"timestamp_utc":now(),"temperature":{"object_temperature_c":32},"motion":{"acceleration_g":{"x":0,"y":0,"z":1},"acceleration_magnitude_g":1}},"wifi":{"scan_status":"ok","access_point_count":4,"access_points":[]}}
    if scenario == "cpu_spike": base["digital"]["cpu"]["usage_percent"] = 96
    if scenario == "thermal_rise": base["physical"]["temperature"]["object_temperature_c"] = 72
    if scenario == "vibration": base["physical"]["motion"]["vibration_rms_g"] = 2.6
    if scenario == "wifi_change": base["wifi"]["access_point_count"] = 20
    if scenario == "combined": base["digital"]["cpu"]["usage_percent"],base["physical"]["temperature"]["object_temperature_c"] = 94, 70
    return store_observation(base)
