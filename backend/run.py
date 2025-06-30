import sys
import os

import atexit
import signal

from api import create_app, socketio
from robot.main import Robot

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
robot = Robot()
app = create_app(robot)

def shutdown_handler(signum=None, frame=None):
    try:
        robot.shutdown_robot()
    except Exception as e:
        print(f"Erreur lors du shutdown: {e}")
    sys.exit(0)

# On passe la fonction SANS les parenthèses
signal.signal(signal.SIGINT, shutdown_handler)
#signal.signal(signal.SIGTERM, shutdown_handler)
#atexit.register(robot.shutdown_robot)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False, threaded=True)
    except Exception as e:
        shutdown_handler()
