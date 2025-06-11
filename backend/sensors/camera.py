import time
import io
import threading
from picamera2 import Picamera2, Preview
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident

class Camera:
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    slow = False  # flag to slow down the camera thread if no clients are connected
    # event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if Camera.thread is None:
            Camera.last_access = time.time()

            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until first frame is available
            # Camera.event.wait()

    def get_frame(self):
        """Return the current camera frame."""
        Camera.last_access = time.time()
        Camera.slow = False

        # wait for a signal from the camera thread
        # Camera.event.wait()
        # Camera.event.clear()

        return Camera.frame

    @staticmethod
    def frames():
        with Picamera2() as camera:
            camera.start()

            # let camera warm up
            time.sleep(2) 

            stream = io.BytesIO()
            try:
                while True:
                    camera.capture_file(stream, format='jpeg')
                    stream.seek(0)
                    yield stream.read()

                    # reset stream for next frame
                    stream.seek(0)
                    stream.truncate()
            finally:
                camera.stop()

    @classmethod
    def _thread(cls):
        """Camera background thread."""
        print('Starting camera thread.')
        frames_iterator = cls.frames()
        try:
            for frame in frames_iterator:
                Camera.frame = frame
                # Camera.event.set()  # send signal to clients
                time.sleep(0)

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds then stop the thread
                if time.time() - Camera.last_access > 10 and not Camera.slow:
                    Camera.slow = True
                    print('Slowing down camera thread due to inactivity.')

                # if no clients are connected, slow down the thread
                if Camera.slow:
                    time.sleep(1)
        finally:
            print('Camera thread stopped.')
            frames_iterator.close()
            Camera.thread = None
            Camera.frame = None
            # Camera.event.set()  # signal that thread has stopped
            
 

 
 

 
 
 
