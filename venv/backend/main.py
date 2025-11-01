from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time
import datetime
import logging
import asyncio
from typing import Optional, List, Dict, Any
from threading import Lock
import io

import numpy as np
import cv2
from backend.utils.camera_utils import Camera
from fastapi import BackgroundTasks
from fastapi import Form
from typing import List as _List


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class BuildStatus:
    def __init__(self):
        self.state: str = "idle"  # idle | queued | running | success | error
        self.last_error: Optional[str] = None
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None
        self._lock = Lock()

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return self.__dict__.copy()

    def update(self, **kwargs):
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

# Defer heavy imports (torch) to runtime to avoid blocking the server startup/reloader.
# We'll initialize the camera lazily when `/video_feed` is requested.
_cam = None
_mtcnn = None
_facenet_resnet = None
_facenet_backend_ready = False

BASE_DIR = Path(__file__).resolve().parent

def get_device():
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def _ensure_facenet_backend():
    """Initialize facenet-pytorch MTCNN and ResNet backbone once."""
    global _mtcnn, _facenet_resnet, _facenet_backend_ready
    if _facenet_backend_ready:
        return _facenet_backend_ready
    try:
        import torch  # noqa: F401
        from facenet_pytorch import InceptionResnetV1, MTCNN
        device = get_device()
        _mtcnn = MTCNN(keep_all=True, device=device)
        _facenet_resnet = InceptionResnetV1(pretrained='vggface2').eval()
        if device == 'cuda':
            _facenet_resnet = _facenet_resnet.cuda()
        _facenet_backend_ready = True
    except Exception as e:
        log.warning(f"Facenet backend not available: {e}")
        _facenet_backend_ready = False
    return _facenet_backend_ready

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:3001", "http://127.0.0.1:3001",
        "http://localhost:5173", "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & templates (use absolute paths so cwd doesn't matter)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Attendance processor (lazy init)
PROCESSOR = None

# In-memory status for encoding build
ENCODING_BUILD_STATUS = BuildStatus()

# Event store for real-time UI logs
EVENT_STORE = []
EVENT_ID_COUNTER = 0
EVENT_LOCK = Lock()

# Attendance CSV dedupe cache is file-based via csv_manager; no in-memory needed


@app.on_event("startup")
async def startup_event():
    # initialize attendance processor if encodings exist
    try:
        from attendance_module.processor import AttendanceProcessor
        from config.settings import ENCODINGS_PATH
        enc_path = str(ENCODINGS_PATH)
        if Path(enc_path).exists():
            global PROCESSOR
            PROCESSOR = AttendanceProcessor(enc_path, event_callback=add_event)
            log.info("AttendanceProcessor loaded with existing encodings.")
    except Exception as e:
        log.warning(f"Could not initialize AttendanceProcessor on startup: {e}")

    # Prefer frontend camera: only start recognition loop if backend camera enabled
    try:
        from database.config.settings import BACKEND_CAMERA_ENABLED
    except Exception:
        BACKEND_CAMERA_ENABLED = False

    try:
        if PROCESSOR and BACKEND_CAMERA_ENABLED:
            async def recognition_loop():
                import cv2
                while True:
                    if _cam is None:
                        await asyncio.sleep(0.5)
                        continue
                    frame_bytes = _cam.get_frame()
                    if frame_bytes is None:
                        await asyncio.sleep(0.2)
                        continue
                    # decode jpeg bytes to numpy BGR
                    arr = np.frombuffer(frame_bytes, dtype=np.uint8)
                    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                    if frame is None:
                        await asyncio.sleep(0.2)
                        continue
                    try:
                        if PROCESSOR:
                            PROCESSOR.process_frame(frame)
                    except Exception as e:
                        log.error(f"Error processing frame in recognition_loop: {e}")
                    await asyncio.sleep(0.6)

            asyncio.create_task(recognition_loop())
            log.info("Recognition loop started (backend camera enabled).")
        else:
            log.info("Backend camera disabled; frontend owns camera capture.")
    except Exception as e:
        log.error(f"Failed to configure recognition_loop on startup: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    device = get_device()
    return templates.TemplateResponse("index.html", {"request": request, "device": device})


@app.get("/attendance", response_class=HTMLResponse)
async def attendance(request: Request):
    device = get_device()
    return templates.TemplateResponse("attendance_dashboard.html", {"request": request, "device": device})


def mjpeg_generator(camera: Camera):
    """Yield multipart MJPEG frames from the given Camera instance."""
    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.get('/video_feed')
def video_feed():
    """Optional MJPEG camera stream. Disabled unless BACKEND_CAMERA_ENABLED is True."""
    try:
        from database.config.settings import BACKEND_CAMERA_ENABLED
    except Exception:
        BACKEND_CAMERA_ENABLED = False
    if not BACKEND_CAMERA_ENABLED:
        return JSONResponse({"error": "Backend camera disabled. Use frontend camera via getUserMedia."}, status_code=403)
    global _cam
    if _cam is None:
        _cam = Camera(src=0)
        _cam.start()
    return StreamingResponse(mjpeg_generator(_cam), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get('/api/attendance/recent')
def api_attendance_recent(limit: int = 10):
    if PROCESSOR is None:
        return {"recent": []}
    recent = PROCESSOR.get_recent(limit)
    return {"recent": [{"name": r[0], "usn": r[1], "time": r[2]} for r in recent if len(r) >= 3]}


@app.get('/api/attendance/csv')
def api_attendance_csv():
    """Download the current attendance CSV file.
    If daily split is enabled, serve today's CSV; otherwise serve the single central CSV.
    Ensures the file exists with a header before returning.
    """
    try:
        from database.config.settings import (
            ATTENDANCE_CSV_PATH,
            ATTENDANCE_DAILY_SPLIT,
        )
        from backend.utils.csv_manager import _ensure_file, resolve_csv_path
        csv_path = resolve_csv_path(ATTENDANCE_CSV_PATH, ATTENDANCE_DAILY_SPLIT)
        _ensure_file(csv_path)
        return FileResponse(path=str(csv_path), media_type='text/csv', filename=csv_path.name)
    except Exception as e:
        log.error(f"Failed to serve attendance CSV: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

def get_utc_now_iso():
    return datetime.datetime.utcnow().isoformat()

def _build_encodings_task(dataset_dir: str, out_path: str, device: str):
    try:
        # mark running
        ENCODING_BUILD_STATUS.update(state='running', last_error=None, started_at=get_utc_now_iso(), finished_at=None)
        log.info("Starting encoding build task.")

        from backend.utils.encoding_utils import build_encodings
        from attendance_module.processor import AttendanceProcessor
        from pathlib import Path
        global PROCESSOR

        build_encodings(dataset_dir, out_path, device=device)

        # if build succeeded and file exists, load into processor so recognition begins immediately
        if Path(out_path).exists():
            log.info("Encoding build finished. Attempting to load new encodings.")
            try:
                PROCESSOR = AttendanceProcessor(str(out_path), event_callback=add_event)
                log.info('Encodings built and processor loaded successfully.')
                ENCODING_BUILD_STATUS.update(state='success', finished_at=get_utc_now_iso())
            except Exception as e:
                error_msg = f'Encodings built but failed to initialize processor: {e}'
                log.error(error_msg)
                ENCODING_BUILD_STATUS.update(state='error', last_error=str(e), finished_at=get_utc_now_iso())
        else:
            error_msg = f"Encoding build ran but output file not found at {out_path}"
            log.error(error_msg)
            ENCODING_BUILD_STATUS.update(state='error', last_error=error_msg, finished_at=get_utc_now_iso())

    except Exception as e:
        log.error(f'Encoding build task failed: {e}', exc_info=True)
        ENCODING_BUILD_STATUS.update(state='error', last_error=str(e), finished_at=get_utc_now_iso())


@app.post('/api/encodings/build')
def api_build_encodings(background_tasks: BackgroundTasks):
    try:
        from config.settings import DATASET_DIR, ENCODINGS_PATH
        device = get_device()
        # mark queued and schedule background task
        ENCODING_BUILD_STATUS.update(state='queued', last_error=None, started_at=None, finished_at=None)
        background_tasks.add_task(_build_encodings_task, str(DATASET_DIR), str(ENCODINGS_PATH), device)
        log.info("Encoding build task queued.")
        return {"status": "started"}
    except Exception as e:
        log.error(f"Failed to queue encoding build task: {e}")
        return {"status": "error", "detail": str(e)}


@app.get('/api/encodings/status')
def api_encodings_status():
    return ENCODING_BUILD_STATUS.get_status()


def add_event(name: str, usn: str = "", event_type: str = "known", location: str = "at gate"):
    """Add an event to the in-memory event store for real-time UI updates."""
    global EVENT_ID_COUNTER
    with EVENT_LOCK:
        EVENT_ID_COUNTER += 1
        event = {
            "id": EVENT_ID_COUNTER,
            "name": name,
            "usn": usn,
            "type": event_type,  # "known" or "unknown"
            "location": location,
            "time": datetime.datetime.now().strftime('%I:%M:%S %p')
        }
        EVENT_STORE.append(event)
        # Keep only last 100 events
        if len(EVENT_STORE) > 100:
            EVENT_STORE.pop(0)
        return event


@app.post('/api/detect_faces')
async def api_detect_faces(file: UploadFile = File(...)):
    """
    Detect and recognize faces in an uploaded image frame.
    Returns JSON with detected faces including bounding boxes, names, and confidence.
    """
    try:
        # Read uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return JSONResponse({"error": "Invalid image"}, status_code=400)
        
        detected_faces = []
        
        # Decide which embedding backend to use based on loaded encodings dimension
        target_dim = None
        if PROCESSOR is not None and isinstance(PROCESSOR.encs, np.ndarray) and PROCESSOR.encs.size > 0:
            if PROCESSOR.encs.ndim == 2:
                target_dim = PROCESSOR.encs.shape[1]

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if target_dim == 512:
            # Use facenet-pytorch MTCNN + ResNet embeddings
            if not _ensure_facenet_backend():
                log.warning("Facenet backend requested but not available; returning no faces.")
                return JSONResponse({"faces": []})

            try:
                from PIL import Image
                img = Image.fromarray(rgb_frame)
                # Detect faces and get boxes
                boxes, probs = _mtcnn.detect(img)
                face_tensors = _mtcnn(img)  # cropped faces as tensors (N, 3, H, W)
                if face_tensors is None:
                    face_tensors = []
                encs = []
                if len(face_tensors) and (boxes is not None):
                    for i in range(len(face_tensors)):
                        face_t = face_tensors[i]
                        with np.errstate(all='ignore'):
                            import torch
                            model_device = next(_facenet_resnet.parameters()).device
                            with torch.no_grad():
                                emb = _facenet_resnet(face_t.unsqueeze(0).to(model_device))
                            emb = emb.detach().cpu().numpy().reshape(-1)
                        encs.append(emb)
                # Build detections
                if boxes is None:
                    boxes = []
                for idx, box in enumerate(boxes):
                    if box is None:
                        continue
                    left, top, right, bottom = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                    name, usn, confidence, status = "Unknown", "", "0%", "unknown"
                    if PROCESSOR is not None and len(encs) > idx and PROCESSOR.encs.size > 0 and PROCESSOR.encs.shape[1] == encs[idx].shape[0]:
                        distances = np.linalg.norm(PROCESSOR.encs - encs[idx], axis=1)
                        min_idx = int(distances.argmin())
                        min_dist = float(distances[min_idx])
                        threshold = 0.8  # facenet usually uses cosine; for L2 use a looser threshold
                        if min_dist <= threshold:
                            from attendance_module.attendance_utils import parse_label
                            label = PROCESSOR.labels[min_idx]
                            name, usn = parse_label(label)
                            confidence = f"{int(max(0.0, (1 - (min_dist/threshold)))*100)}%"
                            status = "known"
                    # Log attendance
                    try:
                        if status == "known":
                            from database.config.settings import (
                                ATTENDANCE_CSV_PATH,
                                ATTENDANCE_DEDUP_MINUTES,
                                ATTENDANCE_DAILY_SPLIT,
                            )
                            from backend.utils.csv_manager import log_if_needed, resolve_csv_path
                            csv_path = resolve_csv_path(ATTENDANCE_CSV_PATH, ATTENDANCE_DAILY_SPLIT)
                            if log_if_needed(csv_path, name, usn, ATTENDANCE_DEDUP_MINUTES):
                                add_event(name, usn, event_type="known", location="auto-detect")
                    except Exception as _e:
                        log.warning(f"Attendance CSV log failed: {_e}")

                    detected_faces.append({
                        "box": [top, right, bottom, left],
                        "name": name,
                        "usn": usn,
                        "confidence": confidence,
                        "status": status,
                        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

            except Exception as e:
                log.error(f"Facenet detect/encode failed: {e}", exc_info=True)
                return JSONResponse({"faces": []})

        else:
            # Default: face_recognition 128-d encodings
            try:
                import face_recognition
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                if PROCESSOR and len(face_encodings) > 0:
                    # Match against known faces if dimensions are compatible
                    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                        name, usn, confidence, status = "Unknown", "", "0%", "unknown"
                        if isinstance(PROCESSOR.encs, np.ndarray) and PROCESSOR.encs.size > 0:
                            if PROCESSOR.encs.ndim == 2 and PROCESSOR.encs.shape[1] == encoding.shape[0]:
                                distances = np.linalg.norm(PROCESSOR.encs - encoding, axis=1)
                                min_idx = int(distances.argmin())
                                min_dist = float(distances[min_idx])
                                threshold = 0.6
                                if min_dist <= threshold:
                                    from attendance_module.attendance_utils import parse_label
                                    label = PROCESSOR.labels[min_idx]
                                    name, usn = parse_label(label)
                                    confidence = f"{int((1 - min_dist) * 100)}%"
                                    status = "known"
                        # Log attendance
                        try:
                            if status == "known":
                                from database.config.settings import (
                                    ATTENDANCE_CSV_PATH,
                                    ATTENDANCE_DEDUP_MINUTES,
                                    ATTENDANCE_DAILY_SPLIT,
                                )
                                from backend.utils.csv_manager import log_if_needed, resolve_csv_path
                                csv_path = resolve_csv_path(ATTENDANCE_CSV_PATH, ATTENDANCE_DAILY_SPLIT)
                                if log_if_needed(csv_path, name, usn, ATTENDANCE_DEDUP_MINUTES):
                                    add_event(name, usn, event_type="known", location="auto-detect")
                        except Exception as _e:
                            log.warning(f"Attendance CSV log failed: {_e}")

                        detected_faces.append({
                            "box": [top, right, bottom, left],
                            "name": name,
                            "usn": usn,
                            "confidence": confidence,
                            "status": status,
                            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                else:
                    # No processor or no faces detected
                    for (top, right, bottom, left) in face_locations:
                        detected_faces.append({
                            "box": [top, right, bottom, left],
                            "name": "Unknown",
                            "usn": "",
                            "confidence": "0%",
                            "status": "unknown",
                            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

            except ImportError:
                log.warning("face_recognition not available for detection")
                return JSONResponse({"faces": []})
        
        return JSONResponse({"faces": detected_faces})
        
    except Exception as e:
        log.error(f"Error in detect_faces: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post('/add_face')
@app.post('/api/add_face')
async def add_face(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    user_id: str = Form(...),
    files: _List[UploadFile] = File(...)
):
    """Add a new user's face images to the dataset and rebuild encodings.
    Expects form-data: name, user_id, files (one or more images).
    """
    try:
        from database.config.settings import DATASET_DIR, ENCODINGS_PATH
        from backend.utils.dataset_manager import ensure_person_dir, save_image_bytes

        target = ensure_person_dir(DATASET_DIR, name, user_id)
        saved = 0
        for f in files:
            content = await f.read()
            # infer ext
            ext = 'jpg'
            if f.filename and '.' in f.filename:
                ext = f.filename.rsplit('.', 1)[-1].lower()
            save_image_bytes(target, content, ext)
            saved += 1

        # queue encodings rebuild
        device = get_device()
        ENCODING_BUILD_STATUS.update(state='queued', last_error=None, started_at=None, finished_at=None)
        background_tasks.add_task(_build_encodings_task, str(DATASET_DIR), str(ENCODINGS_PATH), device)

        add_event(name, user_id, event_type="added", location="dataset")
        return {"status": "ok", "saved": saved, "folder": str(target.name)}
    except Exception as e:
        log.error(f"/add_face failed: {e}", exc_info=True)
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.get('/api/events')
def api_get_events(since: int = 0):
    """Get events since a given event ID for real-time polling."""
    with EVENT_LOCK:
        new_events = [e for e in EVENT_STORE if e['id'] > since]
        return {"events": new_events}


if __name__ == "__main__":
    import uvicorn
    # run without reloader when executed directly to avoid double-import issues
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
