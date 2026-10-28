import json, sqlite3
from contextlib import contextmanager
from .config import DATABASE_PATH

def initialize():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS observations (id TEXT PRIMARY KEY, timestamp_utc TEXT NOT NULL, mode TEXT NOT NULL, payload TEXT NOT NULL, assessment TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_observations_time ON observations(timestamp_utc DESC);
        CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, observation_id TEXT NOT NULL, status TEXT NOT NULL, severity TEXT NOT NULL, title TEXT NOT NULL, evidence TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS experiments (id TEXT PRIMARY KEY, scenario TEXT NOT NULL, status TEXT NOT NULL, result TEXT, created_at TEXT NOT NULL);
        ''')

@contextmanager
def connect():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    try: yield db; db.commit()
    finally: db.close()

def dump(value): return json.dumps(value, default=str)
