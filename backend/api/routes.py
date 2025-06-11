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

# ---------------Servo Motors---------------------------------------
@robot_routes.route('/servo/start', methods=['POST'])
def servo_start_route():
    data = request.get_json() or {}
    try:
        pan, tilt = map(int, data['direction'].split(","))
    except Exception:
        return jsonify({"error": "Invalid format"}), 400
    robot.start_head(pan, tilt)
    return jsonify({"message": "Servo head START"})


@robot_routes.route('/servo/stop', methods=['POST'])
def servo_stop_route():
    robot.stop_head()
    return jsonify({"message": "Servo head STOP"}), 200
def gen():
    """Videostreaminggeneratorfunction."""
    while True:
        frame = robot.get_camera_frame()
        yield(b'--frame\r\n'
            b'Content-Type:image/jpeg\r\n\r\n'+frame+b'\r\n')


@robot_routes.route('/camera')
def video_feed():
    """Videostreamingroute.Putthisinthesrcattributeofanimgtag."""
    return Response(gen(),
        mimetype='multipart/x-mixed-replace;boundary=frame')

@robot_routes.route('/servo/move', methods=['POST'])
def servo_move_route():
    data = request.get_json() or {}
    direction = data.get("direction")
    if not direction:
        return jsonify({"error": "No servo direction provided"}), 400
    try:
        pan, tilt = map(int, direction.split(","))
    except Exception:
        return jsonify({"error": "Invalid servo direction format"}), 400
    robot.movehead(pan, tilt)
    return jsonify({"message": f"Servo moved: pan={pan}, tilt={tilt}"})
