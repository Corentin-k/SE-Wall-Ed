import threading
import time
class Controller:
    def __init__(self, robot):
        self.robot = robot
        self._stop_event = threading.Event()
        self._thread = None
    
    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()


    def _run_loop(self):
        while not self._stop_event.is_set():
            self.update()
            time.sleep(1/20)   # cadence à 20 Hz

    def update(self):
        """ À surcharger dans la sous-classe """
        raise NotImplementedError

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.on_stop()

    

