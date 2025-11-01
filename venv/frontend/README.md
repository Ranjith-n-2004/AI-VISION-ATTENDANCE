# AI Visionary - React Frontend

Modern, responsive React frontend for the AI Visionary Smart Attendance & Security Monitoring System.

## Features

✅ **Auto-start webcam** - No button clicks needed  
✅ **Real-time multi-face detection** - Detects multiple faces simultaneously  
✅ **Bounding boxes with names & confidence** - Visual overlay on detected faces  
✅ **Auto-capture every 1.5 seconds** - Sends frames to backend automatically  
✅ **Live event log** - Real-time attendance/security events  
✅ **Fully responsive** - Works on desktop, tablet, and mobile  
✅ **Dark theme with neon accents** - Modern, futuristic UI  

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling and responsive design
- **Canvas API** - Bounding box overlays
- **MediaDevices API** - Webcam access

## Installation

### Prerequisites
- Node.js 16+ and npm
- FastAPI backend running on http://localhost:8000

### Setup

1. **Install dependencies:**
```powershell
cd frontend
npm install
```

2. **Start development server:**
```powershell
npm run dev
```

The app will open at http://localhost:3000

## Usage

1. **Start the FastAPI backend first:**
```powershell
cd venv
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

2. **Start the React frontend:**
```powershell
cd frontend
npm run dev
```

3. **Open browser:**
Navigate to http://localhost:3000

4. **Grant camera permissions** when prompted

5. **Watch the magic:**
   - Camera feed starts automatically
   - Faces are detected every 1.5 seconds
   - Bounding boxes appear with names and confidence
   - Events log at the bottom shows attendance records

## API Endpoints Used

### POST `/api/detect_faces`
Sends camera frames and receives face detection results.

**Request:** FormData with image file

**Response:**
```json
{
  "faces": [
    {
      "box": [top, right, bottom, left],
      "name": "Ranjith",
      "usn": "1BM19CS001",
      "confidence": "97%",
      "status": "known",
      "timestamp": "2025-10-30 19:22:10"
    }
  ]
}
```

### GET `/api/events?since={id}`
Polls for new attendance/security events.

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "name": "Ranjith",
      "usn": "1BM19CS001",
      "type": "known",
      "location": "in classroom",
      "time": "07:22:10 PM"
    }
  ]
}
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/
│   │   ├── Header.jsx          # App header with title
│   │   ├── CameraFeed.jsx      # Webcam + detection + bounding boxes
│   │   └── EventLog.jsx        # Real-time event footer
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # React entry point
│   └── index.css               # Global styles + Tailwind
├── index.html                  # HTML template
├── vite.config.js              # Vite configuration + proxy
├── tailwind.config.js          # TailwindCSS config
├── postcss.config.js           # PostCSS config
└── package.json                # Dependencies
```

## How It Works

### 1. Camera Auto-Start
On component mount, `CameraFeed` requests webcam access and starts streaming.

### 2. Auto-Capture Loop
Every 1.5 seconds:
- Capture current video frame to canvas
- Convert canvas to JPEG blob
- Send to `/api/detect_faces` via POST

### 3. Face Detection
Backend processes the frame and returns:
- Bounding box coordinates
- Person name (from encodings)
- Confidence percentage
- Status (known/unknown)

### 4. Bounding Box Rendering
Canvas overlay draws:
- Green boxes for known faces
- Red boxes for unknown faces
- Name + confidence labels
- Glow effects

### 5. Event Logging
- Polls `/api/events` every 2 seconds
- Displays new events with fade-in animation
- Color-coded (green=known, red=unknown)

## Customization

### Adjust capture frequency
Edit `CameraFeed.jsx`:
```javascript
const interval = setInterval(captureAndDetect, 1500) // Change 1500ms
```

### Change bounding box colors
Edit `drawBoundingBoxes` in `CameraFeed.jsx`:
```javascript
const color = status === 'known' ? '#10b981' : '#ef4444'
```

### Modify detection threshold
Edit backend `main.py`:
```python
threshold = 0.6  # Lower = stricter matching
```

## Build for Production

```powershell
npm run build
```

Built files will be in `dist/` folder. Serve with any static file server.

## Troubleshooting

### Camera not starting
- Grant camera permissions in browser
- Check if another app is using the camera
- Try different browser (Chrome/Edge recommended)

### No faces detected
- Ensure backend is running and encodings are built
- Check FastAPI logs for errors
- Verify face is clearly visible and well-lit

### CORS errors
- Ensure backend has CORS middleware enabled
- Check frontend is running on port 3000
- Verify Vite proxy is configured correctly

### Bounding boxes not appearing
- Open browser console for errors
- Check `/api/detect_faces` response in Network tab
- Ensure canvas is rendering (check DevTools)

## Development

### Hot Reload
Vite provides instant hot module replacement (HMR). Edit any file and see changes immediately.

### Proxy
Vite proxies `/api/*` requests to `http://127.0.0.1:8000` (FastAPI backend).

### Debugging
- Use React DevTools for component inspection
- Check browser console for errors
- Monitor Network tab for API calls

## Performance Tips

- **Capture interval:** 1-2 seconds is optimal (balance speed/accuracy)
- **Image quality:** 0.8 JPEG quality is good balance
- **Canvas scaling:** Match video dimensions for accuracy
- **Event polling:** 2 seconds prevents excessive requests

---

**Developed by Ranjith N 🚀**
