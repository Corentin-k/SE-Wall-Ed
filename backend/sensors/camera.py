import time
import threading
import cv2
import libcamera
import numpy as np
from picamera2 import Picamera2

# Paramètres optimisés pour réduire la latence
JPEG_QUALITY = 80  # Réduire pour moins de traitement
JPEG_OPTIMIZE = 0  # Désactiver pour plus de vitesse
JPEG_PROGRESSIVE = 0  # Désactiver pour moins de latence
FRAMERATE = 30
RESOLUTION = (640, 480)
BUFFER_COUNT = 1  # Buffer minimal pour réduire la latence

class Camera:
    thread = None
    frame = None
    _stop_event = threading.Event()
    picam: Picamera2 | None = None
    mock_mode = False  # Flag to indicate if running in mock mode

    def __init__(self):
        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self._thread, daemon=True)
            Camera.thread.start()
            # Wait for camera initialization or timeout after 5 seconds
            timeout = 5.0
            start_time = time.time()
            while self.get_frame() is None and (time.time() - start_time) < timeout:
                time.sleep(0.01)
            
            if self.get_frame() is None:
                print("Camera initialization timed out or failed.")

    def get_frame(self):
        return Camera.frame

    @classmethod
    def _generate_mock_frame(cls):
        """Generate a mock frame when no real camera is available."""
        # Create a simple test pattern
        img = np.zeros((RESOLUTION[1], RESOLUTION[0], 3), dtype=np.uint8)
        img[:] = (50, 50, 50)  # Dark gray background
        
        # Add some text
        text = "NO CAMERA DETECTED"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = (img.shape[1] - text_size[0]) // 2
        text_y = (img.shape[0] + text_size[1]) // 2
        cv2.putText(img, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(img, timestamp, (10, 30), font, 0.7, (255, 255, 0), 1)
        
        return img

    @classmethod
    def _thread(cls):
        try:
            # Check if cameras are available
            picam_temp = Picamera2()
            camera_info = picam_temp.global_camera_info()
            picam_temp.close()
            
            if not camera_info:
                print("No cameras detected. Running in mock mode.")
                cls.mock_mode = True
            else:
                cls.picam = Picamera2()
                cfg = cls.picam.create_video_configuration(
                    main={"size": RESOLUTION, "format": "RGB888"},
                    buffer_count=3
                )
                cfg["colour_space"] = libcamera.ColorSpace.Sycc()
                cls.picam.configure(cfg)
                cls.picam.start()
                print("Camera initialized successfully.")
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            print("Running in mock mode.")
            cls.mock_mode = True

        encode_params = [
            int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY,
            int(cv2.IMWRITE_JPEG_OPTIMIZE), JPEG_OPTIMIZE,
            int(cv2.IMWRITE_JPEG_PROGRESSIVE), JPEG_PROGRESSIVE
        ]
        interval = 1.0 / FRAMERATE

        try:
            while not cls._stop_event.is_set():
                if cls.mock_mode:
                    # Generate mock frame
                    img = cls._generate_mock_frame()
                elif cls.picam is None:
                    time.sleep(interval)
                    continue
                else:
                    img = cls.picam.capture_array()  # RGB888 frame
                
                # encode directly without color conversion
                ret, buffer = cv2.imencode('.jpg', img, encode_params)
                if ret:
                    cls.frame = buffer.tobytes()
                time.sleep(interval)
        except Exception as e:
            print(f"Camera capture error: {e}")
        finally:
            if cls.picam:
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
