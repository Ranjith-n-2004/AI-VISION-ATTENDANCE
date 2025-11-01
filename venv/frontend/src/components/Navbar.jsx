export default function Navbar({ cameraActive = true }) {
  return (
    <header className="sticky top-0 z-20 bg-gray-900/80 backdrop-blur border-b border-gray-800">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <h1 className="text-xl md:text-2xl font-extrabold tracking-wider">
          <span className="text-cyan-400">AI</span>
          <span className="text-white">-VISIONARY</span>
        </h1>
        <div className="flex items-center gap-3 text-sm">
          <a
            href="/api/attendance/csv"
            className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white border border-cyan-400/40 transition"
            title="Download attendance CSV"
          >
            ⬇️ Download CSV
          </a>
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${cameraActive ? 'bg-green-400' : 'bg-red-500'}`}></span>
            <span className="text-gray-300">Camera {cameraActive ? 'Active' : 'Inactive'}</span>
          </div>
        </div>
      </div>
    </header>
  )
}
