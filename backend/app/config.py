from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
DATABASE_PATH = Path(os.getenv("QSYNC_DATABASE_PATH", BASE_DIR / "qsync.db"))
API_PREFIX = "/api/v1"
POLICY_VERSION = "consistency-rules-1.0"
FRONTEND_ORIGINS = [origin.strip() for origin in os.getenv("QSYNC_FRONTEND_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
