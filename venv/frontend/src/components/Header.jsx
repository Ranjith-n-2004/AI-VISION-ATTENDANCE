export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800 shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <h1 className="text-3xl md:text-4xl font-bold text-center gradient-text drop-shadow-lg">
          🎯 AI Visionary: Smart Attendance & Security System
        </h1>
        <div className="flex items-center justify-center gap-3 mt-2">
          <div className="flex items-center gap-2 text-cyan-400 text-sm">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span>Auto-Detection Active</span>
          </div>
          <span className="text-gray-500">|</span>
          <div className="text-cyan-400 text-sm">
            Real-time Multi-Face Recognition
          </div>
        </div>
      </div>
    </header>
  )
}
