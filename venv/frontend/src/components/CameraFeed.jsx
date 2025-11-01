import { useEffect, useRef, useState } from 'react'

export default function CameraFeed() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [detections, setDetections] = useState([])
  const [isCapturing, setIsCapturing] = useState(false)
  const streamRef = useRef(null)

  // Initialize webcam on component mount
  useEffect(() => {
    startWebcam()
    return () => stopWebcam()
  }, [])

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 }
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setIsCapturing(true)
      }
    } catch (error) {
      console.error('Error accessing webcam:', error)
      alert('Failed to access webcam. Please grant camera permissions.')
    }
  }

  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
  }

  // Auto-capture and send frames for detection every 1.5 seconds
  useEffect(() => {
    if (!isCapturing) return

    const captureAndDetect = async () => {
      const video = videoRef.current
      const canvas = canvasRef.current
      
      if (!video || !canvas) return

      const ctx = canvas.getContext('2d')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      // Convert canvas to blob
      canvas.toBlob(async (blob) => {
        if (!blob) return

        const formData = new FormData()
        formData.append('file', blob, 'frame.jpg')

        try {
          const response = await fetch('/api/detect_faces', {
            method: 'POST',
            body: formData,
          })
          
          const data = await response.json()
          
          if (data.faces && data.faces.length > 0) {
            setDetections(data.faces)
            drawBoundingBoxes(data.faces, video.videoWidth, video.videoHeight)
          } else {
            setDetections([])
            clearCanvas()
          }
        } catch (error) {
          console.error('Detection error:', error)
        }
      }, 'image/jpeg', 0.8)
    }

    const interval = setInterval(captureAndDetect, 1500)
    return () => clearInterval(interval)
  }, [isCapturing])

  const drawBoundingBoxes = (faces, videoWidth, videoHeight) => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) return

    const ctx = canvas.getContext('2d')
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Scale factors
    const scaleX = canvas.width / videoWidth
    const scaleY = canvas.height / videoHeight

    faces.forEach(face => {
      const { box, name, confidence, status } = face
      const [top, right, bottom, left] = box
      
      // Scale coordinates
      const x = left * scaleX
      const y = top * scaleY
      const width = (right - left) * scaleX
      const height = (bottom - top) * scaleY

      // Draw bounding box
      const color = status === 'known' ? '#10b981' : '#ef4444'
      ctx.strokeStyle = color
      ctx.lineWidth = 3
      ctx.strokeRect(x, y, width, height)

      // Draw label background
      const label = `${name} (${confidence})`
      ctx.font = 'bold 16px Arial'
      const textMetrics = ctx.measureText(label)
      const textWidth = textMetrics.width + 16
      const textHeight = 28

      ctx.fillStyle = color
      ctx.fillRect(x, y - textHeight, textWidth, textHeight)

      // Draw label text
      ctx.fillStyle = '#ffffff'
      ctx.fillText(label, x + 8, y - 8)

      // Add glow effect
      ctx.shadowColor = color
      ctx.shadowBlur = 10
      ctx.strokeRect(x, y, width, height)
      ctx.shadowBlur = 0
    })
  }

  const clearCanvas = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
  }

  return (
    <div className="relative max-w-6xl mx-auto mt-20">
      <div className="relative rounded-2xl overflow-hidden neon-border-cyan shadow-2xl">
        {/* Video element */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-auto max-h-[70vh] object-contain bg-black"
        />
        
        {/* Canvas overlay for bounding boxes */}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
        />
        
        {/* Live indicator */}
        <div className="absolute top-4 right-4 bg-red-500/80 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-2">
          <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
          LIVE
        </div>

        {/* Detection count */}
        {detections.length > 0 && (
          <div className="absolute top-4 left-4 bg-green-500/80 backdrop-blur-sm px-3 py-2 rounded-lg text-sm font-semibold">
            👤 {detections.length} {detections.length === 1 ? 'Face' : 'Faces'} Detected
          </div>
        )}
      </div>

      {/* Detection stats */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700">
          <div className="text-gray-400 text-sm">Total Detections</div>
          <div className="text-2xl font-bold text-cyan-400">{detections.length}</div>
        </div>
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700">
          <div className="text-gray-400 text-sm">Known Faces</div>
          <div className="text-2xl font-bold text-green-400">
            {detections.filter(d => d.status === 'known').length}
          </div>
        </div>
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700">
          <div className="text-gray-400 text-sm">Unknown Faces</div>
          <div className="text-2xl font-bold text-red-400">
            {detections.filter(d => d.status === 'unknown').length}
          </div>
        </div>
      </div>
    </div>
  )
}
