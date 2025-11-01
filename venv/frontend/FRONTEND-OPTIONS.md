# AI Visionary - Frontend Options

This project provides **TWO frontend options** to suit different needs:

## 🎯 Frontend Options Overview

| Feature | React App | HTML/CSS Version |
|---------|-----------|------------------|
| **Technology** | React + Vite + TailwindCSS | Pure HTML + TailwindCSS CDN |
| **Port** | 3000 | 5000 (via serve.py) |
| **Auto-Detection** | ✅ Yes (Multi-face with bounding boxes) | ❌ No (Shows MJPEG stream only) |
| **Bounding Boxes** | ✅ Canvas overlay with names/confidence | ❌ Not available |
| **Real-time Events** | ✅ Yes | ✅ Yes |
| **Build Required** | ✅ npm install + npm run dev | ❌ No build needed |
| **Best For** | Modern browsers, development | Quick demo, no Node.js needed |

---

## 🚀 Option 1: React App (Recommended)

### Features
- ✅ Auto-start webcam (no button clicks)
- ✅ Real-time multi-face detection
- ✅ Bounding boxes with names & confidence
- ✅ Auto-capture every 1.5 seconds
- ✅ Canvas overlay for visual feedback
- ✅ Live detection stats
- ✅ Modern component-based architecture

### Installation

```powershell
# Navigate to frontend folder
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The React app will be available at **http://localhost:3000**

### How It Works
1. Webcam starts automatically on page load
2. Captures frames every 1.5 seconds
3. Sends frames to `/api/detect_faces` endpoint
4. Backend returns face locations, names, confidence
5. React draws bounding boxes on canvas overlay
6. Shows green boxes for known, red for unknown

### File Structure
```
frontend/src/
├── components/
│   ├── Header.jsx          # App header with title
│   ├── CameraFeed.jsx      # Webcam + canvas + detection logic
│   └── EventLog.jsx        # Real-time event footer
├── App.jsx                 # Main app component
├── main.jsx                # Entry point
└── index.css               # TailwindCSS styles
```

### Development
- Hot reload enabled (changes appear instantly)
- React DevTools supported
- Vite proxies `/api/*` to FastAPI backend

---

## 🌐 Option 2: HTML/CSS Version

### Features
- ✅ Pure HTML + TailwindCSS (no build step)
- ✅ MJPEG video stream from FastAPI
- ✅ Real-time event log
- ✅ Build encodings UI
- ✅ Works without Node.js
- ❌ No auto-detection or bounding boxes

### Installation

**No installation needed!** Just serve the files.

### Running the HTML Version

**Method 1: Python HTTP Server (Recommended)**
```powershell
cd frontend
python serve.py
```
Opens at **http://localhost:5000**

**Method 2: Direct File Access**
```powershell
# Just open the file in browser
cd frontend\public
start index.html
```

### File Structure
```
frontend/public/
├── index.html              # Home page with links
└── attendance-html.html    # Attendance dashboard
```

### How It Works
1. Shows MJPEG stream from FastAPI `/video_feed`
2. Polls `/api/events` for new attendance records
3. Displays events in footer with animations
4. Build encodings via button

---

## 📊 Comparison Matrix

### When to Use React App
- ✅ You want **auto-detection** with bounding boxes
- ✅ You need multi-face detection simultaneously
- ✅ You have Node.js installed
- ✅ You want modern development experience
- ✅ You need real-time visual feedback

### When to Use HTML Version
- ✅ Quick demo without installing Node.js
- ✅ Simple attendance monitoring (stream + events)
- ✅ No need for auto-detection
- ✅ Lightweight deployment
- ✅ Works on any browser directly

---

## 🎨 Visual Differences

### React App
```
┌─────────────────────────────────────┐
│  🎯 AI Visionary Header             │
├─────────────────────────────────────┤
│                                     │
│   ┌───────────────────────────┐   │
│   │  Webcam Feed              │   │
│   │  ┌─────────────┐          │   │
│   │  │ Ranjith 97% │ ← Box    │   │
│   │  └─────────────┘          │   │
│   │                           │   │
│   └───────────────────────────┘   │
│                                     │
│   [Total: 2] [Known: 2] [Unknown: 0]│
│                                     │
├─────────────────────────────────────┤
│  📋 Events                          │
│  • Ranjith detected 10:22 AM        │
└─────────────────────────────────────┘
```

### HTML Version
```
┌─────────────────────────────────────┐
│  🎯 AI Visionary Header             │
├─────────────────────────────────────┤
│                                     │
│   ┌───────────────────────────┐   │
│   │  MJPEG Stream             │   │
│   │  (No bounding boxes)      │   │
│   │                           │   │
│   └───────────────────────────┘   │
│                                     │
│   [🔄 Build Encodings] [Status]    │
│                                     │
├─────────────────────────────────────┤
│  📋 Events                          │
│  • Ranjith detected 10:22 AM        │
└─────────────────────────────────────┘
```

---

## 🔧 Running Both Together

You can run **all three** servers simultaneously:

```powershell
# Terminal 1: FastAPI Backend
cd venv
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: React Frontend
cd frontend
npm run dev

# Terminal 3: HTML Static Server
cd frontend
python serve.py
```

Then access:
- **React App:** http://localhost:3000
- **HTML Version:** http://localhost:5000
- **FastAPI Docs:** http://localhost:8000/docs

---

## 🚦 Quick Start Guide

### First Time Setup

1. **Install dependencies:**
```powershell
cd frontend
npm install
```

2. **Choose your preferred method:**

**For React (with auto-detection):**
```powershell
npm run dev
```

**For HTML (simple stream):**
```powershell
python serve.py
```

3. **Add your face:**
```powershell
cd ..
python capture_images.py your_name_usn
```

4. **Build encodings:**
- Open any dashboard
- Click "Build Encodings"
- Wait for success

5. **Start using!**
- React: Faces detected automatically with boxes
- HTML: Stream shows, events appear when recognized

---

## 🎯 Recommendations

**For Production/Demo:**
- Use **React App** for best experience
- Shows off AI capabilities with bounding boxes
- Modern, impressive UI

**For Quick Testing:**
- Use **HTML Version** 
- No build step required
- Works immediately

**For Development:**
- Use **React App** with hot reload
- Easier to modify and extend

---

## 📝 Notes

1. **Backend Required:** Both frontends require FastAPI backend running on port 8000

2. **Camera Permissions:** 
   - React app requests webcam access automatically
   - HTML version shows backend's camera stream (no permission needed)

3. **CORS:**
   - Backend has CORS enabled for both frontends
   - React uses Vite proxy for `/api/*`
   - HTML can be served from any port

4. **Performance:**
   - React: Client-side detection (sends frames every 1.5s)
   - HTML: Server-side processing (continuous MJPEG stream)

---

**Developed by Ranjith N 🚀**
