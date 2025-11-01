# 🚀 AI Visionary - Quick Reference

## 📦 What's in the Frontend Folder?

```
frontend/
├── public/                      # Static HTML files
│   ├── index.html              # Home page (landing)
│   └── attendance-html.html    # HTML/CSS dashboard
├── src/                        # React source code
│   ├── components/
│   │   ├── Header.jsx          # React header
│   │   ├── CameraFeed.jsx      # Webcam + auto-detection
│   │   └── EventLog.jsx        # Event footer
│   ├── App.jsx                 # React main app
│   ├── main.jsx                # React entry
│   └── index.css               # Styles
├── serve.py                    # Static file server for HTML
├── package.json                # Node dependencies
├── vite.config.js              # Vite config
├── tailwind.config.js          # Tailwind config
├── README.md                   # React app docs
└── FRONTEND-OPTIONS.md         # This comparison guide
```

## 🎯 Quick Commands

### Start Everything (Choose Frontend)
```powershell
.\start.ps1
```
Choose option 1 (React) or 2 (HTML) or 3 (Both)

### Manual Start

**Backend Only:**
```powershell
cd venv
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**React App:**
```powershell
cd frontend
npm run dev
# Opens at http://localhost:3000
```

**HTML Version:**
```powershell
cd frontend
python serve.py
# Opens at http://localhost:5000
```

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **React App** | http://localhost:3000 | Auto-detection with bounding boxes |
| **HTML Dashboard** | http://localhost:5000 | Simple stream + events |
| **FastAPI Docs** | http://localhost:8000/docs | API documentation |
| **Video Stream** | http://localhost:8000/video_feed | MJPEG stream |

## 🎨 Frontend Comparison

### React App Features
✅ Auto-start webcam  
✅ Multi-face detection  
✅ Bounding boxes with names  
✅ Confidence percentages  
✅ Real-time canvas overlay  
✅ Detection statistics  
✅ Auto-capture every 1.5s  

### HTML Version Features
✅ MJPEG video stream  
✅ Real-time event log  
✅ Build encodings UI  
✅ No Node.js required  
✅ Instant startup  
❌ No bounding boxes  
❌ No auto-detection  

## 📊 Which One to Use?

### Use React App When:
- Demonstrating AI capabilities
- Need visual feedback (bounding boxes)
- Want modern UX
- Have Node.js installed
- Need multi-face detection

### Use HTML Version When:
- Quick demo/testing
- No Node.js available
- Simple stream viewing
- Minimal setup needed
- Deployment on static host

## 🔧 Customization

### Change Detection Speed (React)
Edit `frontend/src/components/CameraFeed.jsx`:
```javascript
const interval = setInterval(captureAndDetect, 1500) // milliseconds
```

### Adjust Confidence Threshold (Backend)
Edit `venv/main.py` in `/api/detect_faces`:
```python
threshold = 0.6  # Lower = stricter
```

### Modify Bounding Box Colors (React)
Edit `frontend/src/components/CameraFeed.jsx`:
```javascript
const color = status === 'known' ? '#10b981' : '#ef4444'
```

## 🐛 Common Issues

### React app won't start
```powershell
# Install dependencies first
cd frontend
npm install
```

### HTML version shows blank page
- Make sure FastAPI backend is running on port 8000
- Check browser console for CORS errors

### No faces detected
- Ensure encodings are built
- Check backend logs for errors
- Verify face is well-lit and clearly visible

### Camera not starting (React)
- Grant camera permissions in browser
- Close other apps using camera
- Try Chrome/Edge browser

## 📝 Development Workflow

1. **First time:**
```powershell
cd frontend
npm install
```

2. **Every session:**
```powershell
# Use start script (recommended)
.\start.ps1

# Or manual:
# Terminal 1: Backend
cd venv
python -m uvicorn main:app --reload

# Terminal 2: React
cd frontend
npm run dev
```

3. **Add people:**
```powershell
python capture_images.py name_usn
```

4. **Build encodings:**
- Click "Build Encodings" in any dashboard
- Wait for "Status: success"

5. **Test:**
- React: http://localhost:3000 (auto-detection)
- HTML: http://localhost:5000 (stream)

## 🎯 Production Deployment

### React App
```powershell
cd frontend
npm run build
# Deploy 'dist/' folder to static host
```

### HTML Version
Just copy `frontend/public/*.html` to any web server

### Backend
```powershell
cd venv
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 💡 Pro Tips

1. **Both frontends work simultaneously** - choose based on use case
2. **React has hot reload** - changes appear instantly during development
3. **HTML version needs no build** - fastest for quick demos
4. **Use React for demos** - bounding boxes impress audiences
5. **Use HTML for testing** - simpler, faster startup

---

**Need Help?** Check:
- `frontend/README.md` - React app details
- `frontend/FRONTEND-OPTIONS.md` - Feature comparison
- Main `README.md` - Project overview

**Developed by Ranjith N 🚀**
