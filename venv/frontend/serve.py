"""
Simple HTTP server to serve the HTML/CSS frontend files
Run this to access the static HTML version at http://localhost:5000
"""
import http.server
import socketserver
from pathlib import Path

PORT = 5000
DIRECTORY = Path(__file__).parent / "public"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ HTML Frontend Server running at http://localhost:{PORT}")
        print(f"📁 Serving files from: {DIRECTORY}")
        print(f"\n🌐 Open your browser to:")
        print(f"   Home: http://localhost:{PORT}/")
        print(f"   Attendance: http://localhost:{PORT}/attendance-html.html")
        print(f"\n⚠️  Make sure FastAPI backend is running on port 8000!")
        print(f"\nPress Ctrl+C to stop the server\n")
        httpd.serve_forever()
