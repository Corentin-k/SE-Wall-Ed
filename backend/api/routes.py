from flask import Blueprint, request, jsonify, Response
from flask_socketio import SocketIO, emit
from . import socketio
from sensors import Camera


robot_routes = Blueprint('robot_routes', __name__)
robot = None

def map_range(x,in_min,in_max,out_min,out_max):
  return (x - in_min)/(in_max - in_min) *(out_max - out_min) +out_min

def set_robot_instance(r):
    global robot
    robot = r
    
@robot_routes.route('/motor/stop', methods=['POST'])
def motor_stop_route():
    robot.stop()
    return jsonify({"message": "Motor stopped"})


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

def gen():
    """Fonction génératrice de flux vidéo."""
    camera = Camera()
    while True:
        # frame = robot.get_camera_frame()
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type:image/jpeg\r\n\r\n'+frame+b'\r\n')
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

@socketio.on('motor_move')
def motor_move_route(data):
    speed = data.get("speed", 50)
    robot.move_robot(speed)

@socketio.on('turn_wheel')
def turn_wheel(data):
    direction = data.get("direction", "forward")

    angle = 0
    if direction == "left":
        angle = 37
    elif direction == "right":
        angle = -37
    
    angle = map_range(angle, -98, 82, 0, 180)
    robot.change_direction(angle)

@socketio.on('move_head')
def handle_move_servo(data):
    """Handle servo movement requests from the frontend via WebSocket."""
    pan = data.get('pan', 0)
    tilt = data.get('tilt', 0)
    
    try:
        pan = int(pan)
        tilt = int(tilt)
    except ValueError:
        emit('error', {"error": "Invalid pan or tilt value. Must be integer."})
        return

    robot.start_head(pan, tilt)
    emit('servo_moved', {"message": f"Servo head started moving: pan={pan}, tilt={tilt}"})

@socketio.on('stop_head')
def handle_stop_servo():
    """Handle servo stop requests from the frontend via WebSocket."""
    robot.stop_head()
    emit('servo_stopped', {"message": "Servo head stopped"})

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Connected'})

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    emit('message', {'data': 'Message received'})

