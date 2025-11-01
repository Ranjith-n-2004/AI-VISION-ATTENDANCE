# 🎯 AI-VISIONARY: Smart AI-based Attendance System (React + FastAPI)

End-to-end attendance system with real-time multi-face recognition, CSV logging (with dedupe), and a modern React UI. Camera runs in the browser by default for reliability; backend streaming is available as an option.

## ✨ What’s Included

- Real-time multi-face detection via webcam (no button needed)
- Face matching against dataset encodings
- CSV attendance logging: Name, ID, Time, Date (with 10-minute dedupe)
- Add new users (faces) from the UI, stored in structured folders
- Live event footer showing recognitions and add-face events
- Optional daily CSV split (attendance_YYYY-MM-DD.csv)

## 📁 Project Structure (key)

```
AI-VISIONARY/
└─ venv/
   ├─ backend/
   │  ├─ main.py                  # FastAPI app (entry point)
   │  ├─ utils/
   │  │  ├─ csv_manager.py        # CSV logging and dedupe
   │  │  ├─ dataset_manager.py    # Add-face dataset helpers
   │  │  └─ encoding_utils.py     # Build/load encodings
   │  ├─ dataset/                 # Known faces (Name_(ID)/images)
   │  ├─ encodings/encodings.pkl  # Generated encodings
   │  └─ attendance.csv           # Central CSV (if daily split disabled)
   ├─ database/
   │  └─ config/settings.py       # Global settings
   ├─ attendance_module/          # Legacy processor (optional)
   └─ frontend/
      ├─ src/components/          # CameraFeed, AddFaceForm, Navbar, EventFooter
      ├─ vite.config.js           # Proxies /api → http://127.0.0.1:8000
      └─ package.json
```

## 🚀 Run It (Windows PowerShell)

```powershell
# 1) Backend
cd "C:\Users\RANJITH N\OneDrive\Desktop\AI-VISIONARY\venv"
.\n+Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# 2) Frontend (new PowerShell tab)
cd "C:\Users\RANJITH N\OneDrive\Desktop\AI-VISIONARY\venv\frontend"
npm install
npm start
```

Notes:
- If port 3000 is busy, Vite will switch to 3001 automatically; CORS is pre-configured for 3000/3001/5173.
- The frontend proxies API calls via `/api` to the backend.

## 🧠 How It Works

1) CameraFeed.jsx captures frames from the browser with getUserMedia and periodically POSTs to `/api/detect_faces`.
2) The backend detects and matches faces (face_recognition) and logs known matches to CSV, deduping within 10 minutes.
3) AddFaceForm.jsx records 3–5 snapshots and sends them to `/api/add_face`. The backend saves images under `backend/dataset/Name_(ID)/` and rebuilds encodings in the background.
4) Live events (recognitions and add-face) appear in the EventFooter via polling `/api/events`.

Optional: Set `BACKEND_CAMERA_ENABLED=True` in `venv/database/config/settings.py` to let the backend own the webcam and expose `/video_feed`. Off by default (browser camera preferred).

## ⚙️ Configuration

Edit `venv/database/config/settings.py`:

```python
# Dataset and encodings
DATASET_DIR = PROJECT_ROOT / "backend" / "dataset"
ENCODINGS_PATH = PROJECT_ROOT / "backend" / "encodings" / "encodings.pkl"

# Attendance CSV
ATTENDANCE_CSV_PATH = PROJECT_ROOT / "backend" / "attendance.csv"
ATTENDANCE_DAILY_SPLIT = False       # True → attendance_YYYY-MM-DD.csv
ATTENDANCE_DEDUP_MINUTES = 10

# Camera ownership
BACKEND_CAMERA_ENABLED = False       # True to stream /video_feed from backend
```

## � Add New Face (UI)

1) Open the app (http://localhost:3000 or 3001)
2) Enter Name and ID (e.g., Ranjith N and 1TD24CS227)
3) Click Capture 3–5 times and then Save Face(s)
4) The folder `backend/dataset/Ranjith N_(1TD24CS227)/` is created and images saved
5) Encodings rebuild automatically; recognition works on next frames

## 🧪 Quick API Checks (optional)

```powershell
# Trigger build encodings manually
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/encodings/build -Method POST
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/encodings/status -Method GET | Format-List

# Poll events
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/events -Method GET
```

## 🧩 Dependencies

See `requirements.txt`. On Windows, dlib (for face_recognition) may need Conda or a prebuilt wheel. If `python-multipart` is missing, install it to handle form uploads.

## 🐛 Troubleshooting

- Webcam not accessible in browser → Grant permissions; ensure no other app is using the camera.
- CORS errors → Make sure you start the backend first; frontend is proxied to `/api`.
- No recognitions → Ensure encodings exist (they are rebuilt after adding a face); check backend logs for errors.
- CSV not written → Verify write permissions under `venv/backend`.

## � Optional Enhancement

Set `ATTENDANCE_DAILY_SPLIT=True` to generate `attendance_YYYY-MM-DD.csv` files automatically next to `attendance.csv`.

---

Developed by Ranjith N 🚀
