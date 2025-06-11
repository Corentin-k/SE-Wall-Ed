import logging
from api import create_app

from robot.main import Robot
robot = Robot()
app = create_app(robot)
@app.teardown_appcontext
def cleanup(exception=None):
    robot.leds.destroy()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
   
  
    app.run(host="0.0.0.0", port=5000, debug=True)
