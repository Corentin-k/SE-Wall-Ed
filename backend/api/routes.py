from flask import Blueprint, request, jsonify, Response
from flask_socketio import SocketIO, emit
from . import socketio
from sensors import Camera
import base64
import time
import threading
robot_routes = Blueprint('robot_routes', __name__)
robot = None
police_on = False 

def map_range(x,in_min,in_max,out_min,out_max):
  return (x - in_min)/(in_max - in_min) *(out_max - out_min) +out_min

def set_robot_instance(r):
    global robot
    robot = r
    
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

# ------------------Root Settings -------------------------------
@robot_routes.route('/set_speed', methods=['POST'])
def set_speed_route():
    data = request.get_json() or {}
    speed = data.get("speed", 50)
    if not isinstance(speed, int) or speed < 0:
        return jsonify({"error": "Invalid speed value"}), 400
    try:
        robot.update_speed(speed)
        return jsonify({"message": f"Speed set to {speed}"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500   
# ---------------Root Mode---------------------------------------

@robot_routes.route('/mode/police', methods=['POST'])
def set_mode_police():
    global police_on
    if not police_on:
        robot.mode_police()
        police_on = True
        msg = "Mode police activé"
    else:
        robot.stop_police()      
        police_on = False
        msg = "Mode police désactivé"
    return jsonify({"message": msg, "police_on": police_on})


@robot_routes.route('/mode/automatic_processing', methods=['POST'])
def set_mode_automatic_processing():
    data = request.get_json() or {}
    mode = data.get("mode", "start")
    if mode == "start":
        robot.start_automatic_processing()
        return jsonify({"message": "Mode traitement automatique démarré"})
    elif mode == "stop":
        robot.stop_robot()
        robot.init_servo_head()
        return jsonify({"message": "Mode traitement automatique arrêté"})
    else:
        return jsonify({"error": "Mode non reconnu"}), 400


# ---------------Camera Streaming---------------------------------------
#@robot_routes.route('/camera')
#def video_feed():
#    """Videostreamingroute.Putthisinthesrcattributeofanimgtag."""
#    return Response(gen(),
#        mimetype='multipart/x-mixed-replace;boundary=frame')
@robot_routes.route('/camera')
def video_feed():
    """Flux MJPEG continu"""
    def gen():
        while True:
            frame = robot.get_camera_frame()
            if not frame:
                time.sleep(0.01)
                continue
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )
            # throttle
            time.sleep(1/30)
    response = Response(gen(), mimetype='multipart/x-mixed-replace;boundary=frame')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
    
def gen():
    """Fonction génératrice de flux vidéo."""
    while True:
        frame = robot.get_camera_frame()
        yield(b'--frame\r\n'
              b'Content-Type:image/jpeg\r\n\r\n'+frame+b'\r\n')

# ---------------WebSocket Routes---------------------------------------
@socketio.on('motor_move')
def motor_move_route(data):
    speed = data.get("speed", 50)
    robot.move_robot(speed)

@socketio.on('turn_wheel')
def turn_wheel(data):
    direction = data.get("direction", "forward")

    angle = 0
    if direction == "left":
        angle = 30
    elif direction == "right":
        angle = -30
    
    angle = map_range(angle, -92, 82, 0, 180)
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
    #print('Client connected')
    emit('message', {'data': 'Connected'})

@socketio.on('message')
def handle_message(data):
    #print('Received message:', data)
    emit('message', {'data': 'Message received'})

# --- NEW: Line Tracking WebSocket Events ---
@socketio.on('start_line_tracking')
def handle_start_line_tracking():
    """
    Handles requests from the frontend via WebSocket to start line tracking.
    """
    if robot:
        try:
            robot.start_line_tracking()
            emit('line_tracking_status', {"message": "Line tracking started", "active": True})
        except Exception as e:
            emit('error', {"error": f"Failed to start line tracking: {str(e)}"})
    else:
        emit('error', {"error": "Robot instance not set."})

@socketio.on('stop_line_tracking')
def handle_stop_line_tracking():
    """
    Handles requests from the frontend via WebSocket to stop line tracking.
    """
    robot.stop_line_tracking()


def video_stream():
    """Generates video frames for the video stream."""
    while True:
        frame = robot.get_camera_frame()
        if not frame:
            time.sleep(0.01)
            continue
        stringData = base64.b64encode(frame).decode('utf-8')
        b64_src = 'data:image/jpeg;base64,'
        stringData = b64_src + stringData
        yield stringData

def video_stream_thread():
    last_time = time.time()
    for frame in video_stream():  # frame is base64-encoded string
        socketio.emit('video', frame, namespace='/video_stream')
        # print("frame sended in ", time.time() - last_time, "ms")
        time.sleep(1/60)  # Optional: control FPS
        last_time = time.time()

# @socketio.on('connect', namespace='/video_stream')
# def handle_video_stream_connect(auth):  # Accept the 'auth' argument
#     threading.Thread(target=video_stream_thread, daemon=True).start()
