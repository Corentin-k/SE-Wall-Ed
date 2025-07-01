import threading
import time
class Controller:
    def __init__(self, robot):
        self.robot = robot
        self._stop_event = threading.Event()
        self._thread = None
    
    def start_controller(self,update_interval: float = 1/50):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop,args=(update_interval,),
                                         daemon=True)
        self._thread.start()
        self.start()
    def start():
        pass


    def _run_loop(self, interval: float):
        while not self._stop_event.is_set():
            try:
                self.update()
            except Exception as e:
                print(f"Erreur dans la boucle du contrôleur : {e}")
                break
            time.sleep(interval)
        self.on_stop()

    def update(self):
        raise NotImplementedError

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.on_stop()
    def on_stop(self):
        self.robot.motor.smooth_speed(0)
        self.robot.motor_servomotor.set_angle(90)
