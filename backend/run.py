# run.py
import logging
import atexit
import signal
import sys
from api import create_app
from robot.main import Robot

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")

    robot = Robot()
    app = create_app(robot)

    # on enregistre la destruction pour la fin de vie du process
    def cleanup_and_exit(*args):
        robot.leds.destroy()
        robot.camera.destroy()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    atexit.register(lambda: robot.leds.destroy())

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False, threaded=True)
