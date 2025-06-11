import logging
from api import create_app

from robot.main import Robot

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    robot = Robot()
    app = create_app(robot)
    app.run(host="0.0.0.0", port=5000, debug=True)
