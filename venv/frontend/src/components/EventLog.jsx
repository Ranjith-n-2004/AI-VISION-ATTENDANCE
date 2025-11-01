export default function EventLog({ events }) {
  return (
    <footer className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-sm border-t border-gray-800 shadow-2xl">
      <div className="container mx-auto px-4 py-4 max-h-80 overflow-y-auto" id="log_container">
        <h3 className="text-lg font-bold text-cyan-400 mb-3 sticky top-0 bg-gray-900/95 py-2">
          📋 Real-Time Detection Events
        </h3>
        <div className="space-y-2">
          {events.length === 0 ? (
            <div className="text-gray-500 text-sm text-center py-4">
              Waiting for detection events...
            </div>
          ) : (
            events.map((event, index) => (
              <div
                key={`${event.id}-${index}`}
                className={`animate-fadeIn p-3 rounded-lg border transition-all duration-300 hover:scale-[1.02] ${
                  event.type === 'known'
                    ? 'bg-green-900/30 border-green-500/50 neon-border'
                    : 'bg-red-900/30 border-red-500/50 neon-border-red'
                }`}
              >
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">👤</span>
                    <span
                      className={`font-semibold ${
                        event.type === 'known' ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {event.name}
                      {event.usn && ` (${event.usn})`}
                    </span>
                    <span className="text-gray-400 text-sm">
                      {event.location || 'detected'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <span>🕒</span>
                    <span>{event.time}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Watermark */}
      <div className="text-right px-4 py-2 text-xs text-gray-600 border-t border-gray-800">
        Developed by Ranjith N 🚀
      </div>
    </footer>
  )
}
