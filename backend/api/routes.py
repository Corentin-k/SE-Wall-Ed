from flask import Blueprint, request, jsonify, Response



robot_routes = Blueprint('robot_routes', __name__)
robot = None

def set_robot_instance(r):
    global robot
    robot = r
    
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

# ---------------LED RGB---------------------------------------
@robot_routes.route('/led/color', methods=['POST'])
def set_led_color_route():
    data = request.get_json() or {}
    color_hex = data.get("color")
    if not color_hex:
        return jsonify({"error": "No color provided"}), 400
    try:
        robot.led(color_hex)
        return jsonify({"message": f"LED color set to {color_hex}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------Camera Streaming---------------------------------------
@robot_routes.route('/camera')
def video_feed():
    """Videostreamingroute.Putthisinthesrcattributeofanimgtag."""
    return Response(gen(),
        mimetype='multipart/x-mixed-replace;boundary=frame')

# ---------------Servo Motors---------------------------------------
@robot_routes.route('/servo/start', methods=['POST'])
def servo_start_route():
    data = request.get_json() or {}
    # Expect 'pan' and 'tilt' directly as integers from the frontend
    pan = data.get('pan', 0)
    tilt = data.get('tilt', 0)

    try:
        # Ensure they are integers, although the frontend should send them as such
        pan = int(pan)
        tilt = int(tilt)
    except ValueError:
        return jsonify({"error": "Invalid pan or tilt value. Must be integer."}), 400
    
    # Call robot.start_head with the combined pan and tilt values
    # This will handle stopping any existing head movement thread and starting a new one
    # with the combined directions, enabling simultaneous control.
    robot.start_head(pan, tilt)
    return jsonify({"message": f"Servo head movement started: pan={pan}, tilt={tilt}"})

@robot_routes.route('/servo/stop', methods=['POST'])
def servo_stop_route():
    robot.stop_head()
    return jsonify({"message": "Servo head STOP"}), 200
