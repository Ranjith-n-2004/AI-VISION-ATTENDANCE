import { useEffect, useRef, useState } from 'react'

export default function AddFaceForm() {
  const [name, setName] = useState('')
  const [userId, setUserId] = useState('')
  const [captured, setCaptured] = useState([]) // blobs
  const [saving, setSaving] = useState(false)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)

  useEffect(() => {
    ;(async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          streamRef.current = stream
        }
      } catch (e) {
        console.error('Camera error', e)
      }
    })()
    return () => {
      if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
    }
  }, [])

  const capture = () => {
    const v = videoRef.current
    const c = canvasRef.current
    if (!v || !c) return
    const w = v.videoWidth
    const h = v.videoHeight
    c.width = w
    c.height = h
    const ctx = c.getContext('2d')
    ctx.drawImage(v, 0, 0, w, h)
    c.toBlob((blob) => {
      if (!blob) return
      setCaptured(prev => prev.length < 5 ? [...prev, blob] : prev)
    }, 'image/jpeg', 0.9)
  }

  const reset = () => setCaptured([])

  const submit = async () => {
    if (!name || !userId || captured.length === 0) {
      alert('Enter name, ID and capture at least 1 image (prefer 3-5).')
      return
    }
    setSaving(true)
    try {
      const fd = new FormData()
      fd.append('name', name)
      fd.append('user_id', userId)
      captured.forEach((b, i) => fd.append('files', b, `capture_${i+1}.jpg`))
  // Use /api prefix so Vite dev server proxies to backend
  const res = await fetch('/api/add_face', { method: 'POST', body: fd })
      const data = await res.json()
      if (data.status === 'ok') {
        alert(`${name}_(${userId}) added successfully!`) // simple toast
        reset()
      } else {
        alert('Failed: ' + (data.detail || 'unknown error'))
      }
    } catch (e) {
      console.error(e)
      alert('Request failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bg-gray-800/40 border border-gray-700 rounded-xl p-4">
      <h3 className="text-lg font-semibold mb-3">Add New Face</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-gray-300 mb-1">Name</label>
          <input className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2" value={name} onChange={e=>setName(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-gray-300 mb-1">ID</label>
          <input className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2" value={userId} onChange={e=>setUserId(e.target.value)} />
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
        <div className="md:col-span-2">
          <div className="relative rounded overflow-hidden border border-gray-700 bg-black">
            <video ref={videoRef} autoPlay playsInline muted className="w-full h-auto" />
            <canvas ref={canvasRef} className="hidden" />
          </div>
          <div className="flex gap-2 mt-3">
            <button onClick={capture} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 rounded">Capture</button>
            <button onClick={reset} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded">Reset</button>
            <button disabled={saving} onClick={submit} className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded disabled:opacity-50">
              {saving ? 'Saving...' : 'Save Face(s)'}
            </button>
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-400 mb-2">Captured ({captured.length}/5)</div>
          <div className="grid grid-cols-2 gap-2">
            {captured.map((b, i) => (
              <img key={i} src={URL.createObjectURL(b)} alt={`cap_${i}`} className="rounded border border-gray-700" />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
