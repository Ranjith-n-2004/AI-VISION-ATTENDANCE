import threading
import cv2
import time


class Camera:
    """Background camera reader that provides latest JPEG frames."""
    def __init__(self, src=0, width=None, height=None):
        self.src = src
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(self.src)
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            # encode as JPEG bytes
            ret2, jpeg = cv2.imencode('.jpg', frame)
            if ret2:
                self.frame = jpeg.tobytes()

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
