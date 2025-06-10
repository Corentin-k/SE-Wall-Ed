from flask import Blueprint, request, jsonify
from robot.main import Robot  # Import de la classe Robot

robot = Robot()  # Instance unique partagée
robot_routes = Blueprint('robot_routes', __name__)

@robot_routes.route('/motor/stop', methods=['POST'])
def motor_stop_route():
    robot.stop()
    return jsonify({"message": "Motor stopped"})

@robot_routes.route('/motor/move', methods=['POST'])
def motor_move_route():
    data = request.get_json() or {}
    direction = data.get("direction")
    speed = data.get("speed", 50)  # valeur par défaut

    if direction == "forward":
        robot.move_forward(speed)
        return jsonify({"message": f"Robot moving forward at speed {speed}"})
    elif direction == "backward":
        robot.move_backward(speed)
        return jsonify({"message": f"Robot moving backward at speed {speed}"})
    elif direction == "left":
        robot.turn_left(speed)
        return jsonify({"message": f"Robot turning left at speed {speed}"})
    elif direction == "right":
        robot.turn_right(speed)
        return jsonify({"message": f"Robot turning right at speed {speed}"})
    else:
        return jsonify({"error": f"Invalid direction '{direction}'"}), 400


@robot_routes.route('/motor/speed', methods=['POST'])
def motor_speed_route():
    data = request.get_json()
    speed = data.get("speed")
    if speed is not None:
        robot.motor.set_speed(speed)
        return jsonify({"message": f"Motor speed set to {speed}"})
    else:
        return jsonify({"error": "Speed not provided"}), 400
