import time
import threading
import cv2
import libcamera
from picamera2 import Picamera2

# Paramètres d'encodage au maximum de la caméra
JPEG_QUALITY = 100
JPEG_OPTIMIZE = 1
JPEG_PROGRESSIVE = 1
FRAMERATE = 30
RESOLUTION = (640, 480)

class Camera:
    thread = None
    frame = None
    _stop_event = threading.Event()
    picam: Picamera2 | None = None

    def __init__(self):
        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self._thread, daemon=True)
            Camera.thread.start()
            while self.get_frame() is None:
                time.sleep(0.01)

    def get_frame(self):
        return Camera.frame

    @classmethod
    def _thread(cls):
        cls.picam = Picamera2()
        cfg = cls.picam.create_video_configuration(
            main={"size": RESOLUTION, "format": "RGB888"},
            buffer_count=3
        )
        cfg["colour_space"] = libcamera.ColorSpace.Sycc()
        cls.picam.configure(cfg)
        cls.picam.start()

        encode_params = [
            int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY,
            int(cv2.IMWRITE_JPEG_OPTIMIZE), JPEG_OPTIMIZE,
            int(cv2.IMWRITE_JPEG_PROGRESSIVE), JPEG_PROGRESSIVE
        ]
        interval = 1.0 / FRAMERATE

        try:
            while not cls._stop_event.is_set():
                img = cls.picam.capture_array()  # RGB888 frame
                # encode directly without color conversion
                ret, buffer = cv2.imencode('.jpg', img, encode_params)
                if ret:
                    cls.frame = buffer.tobytes()
                time.sleep(interval)
        finally:
            cls.picam.stop()
            cls.frame = None

    @classmethod
    def shutdown(cls):
        cls._stop_event.set()

        
        if cls.picam:
            try:
                cls.picam.stop()
            except Exception:
                pass
            try:
                cls.picam.close()
            except Exception:
                pass
            finally:
                cls.picam = None

        
        if cls.thread:
            cls.thread.join(timeout=2.0)
            cls.thread = None

        
        cls.frame = None
        cls._stop_event.clear()
        print("Camera shutdown complete.")
