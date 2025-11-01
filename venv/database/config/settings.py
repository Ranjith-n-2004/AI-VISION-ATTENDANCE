"""Project settings and runtime configuration.
Auto-detects device (cuda/cpu) and exposes common paths and thresholds.
"""
from pathlib import Path
import os

try:
    import torch
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    DEVICE = "cpu"

ROOT = Path(__file__).resolve().parents[1]

# Updated paths to reflect new repo layout after refactor:
PROJECT_ROOT = ROOT.parent  # points to venv/

# Match prompt structure: keep dataset and attendance.csv under backend/
DATASET_DIR = PROJECT_ROOT / "backend" / "dataset"
ENCODINGS_PATH = PROJECT_ROOT / "backend" / "encodings" / "encodings.pkl"

# Logs (legacy attendance module location; kept for compatibility with AttendanceProcessor)
ATTENDANCE_LOG_DIR = PROJECT_ROOT / "attendance_module" / "logs"
SECURITY_LOG_DIR = None
DETECTED_FACES_DIR = None

# Attendance CSV (as per prompt, keep under backend/)
ATTENDANCE_CSV_PATH = PROJECT_ROOT / "backend" / "attendance.csv"

# Optional: Split attendance into daily CSV files (attendance_YYYY-MM-DD.csv)
ATTENDANCE_DAILY_SPLIT = False

# Face recognition thresholds
# For facenet/arcface style embeddings, euclidean threshold ~0.8; tune per dataset
FACE_MATCH_TOLERANCE = 0.8

# Re-log window to avoid duplicate attendance within N minutes
ATTENDANCE_DEDUP_MINUTES = 10

# Liveness (EAR) thresholds
EAR_THRESHOLD = 0.20
EAR_CONSEC_FRAMES = 3

# YOLO device (use same device detected above)
YOLO_DEVICE = DEVICE

# Other
os.makedirs(ATTENDANCE_LOG_DIR, exist_ok=True)
# Security module removed; no directories needed
os.makedirs(DATASET_DIR, exist_ok=True)
ATTENDANCE_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
# Ensure encodings directory exists
(ENCODINGS_PATH.parent).mkdir(parents=True, exist_ok=True)

# Camera ownership: prefer frontend (browser) to capture and POST frames to backend.
# Set to True only if you want the backend to open the webcam and stream /video_feed.
BACKEND_CAMERA_ENABLED = False
