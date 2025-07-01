from flask import Blueprint, request, jsonify, Response
from flask_socketio import SocketIO, emit
from robot.line_tracking_processing import LineTrackingController
from robot.color_detection import ColorDetectionController
#from robot.radar_processing import RadarController

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
    
    #angle = map_range(angle, -106, 73, 0, 180)
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

@socketio.on('mode')
def handle_mode(data):
    mode = data.get('mode', 'default')
    if mode == 'ligne_tracking':
        ctrl = LineTrackingController(robot)
    elif mode == 'automatic_processing':
        ctrl = RadarController(robot)
    else:
        ctrl = None
    robot.set_controller(ctrl)
    emit('mode_status', {'mode': mode, 'active': bool(ctrl),
                        'message': f"Mode {mode} {'activé' if ctrl else 'arrêté'}"}, broadcast=False)


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
@socketio.on('emergency')
def handle_emergency(data):
    active = data.get('active', False)
    robot.set_emergency_mode(active)
    emit('mode_status', {'mode': 'default', 'active': False, 
         'message': f"Mode emergency {'activé' if active else 'désactivé'}"}, broadcast=True)
    emit('emergency', {'active': active}, broadcast=True)

# ---------------Color Detection Routes---------------------------------------
@robot_routes.route('/color_detection/toggle', methods=['POST'])
def toggle_color_detection():
    """Active/désactive la détection de couleur"""
    data = request.get_json() or {}
    enabled = data.get("enabled", True)
    
    try:
        robot.enable_color_detection(enabled)
        return jsonify({
            "message": f"Détection de couleur {'activée' if enabled else 'désactivée'}",
            "enabled": enabled
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@robot_routes.route('/color_detection/status', methods=['GET'])
def get_color_detection_status():
    """Récupère l'état de la détection de couleur et les couleurs détectées"""
    try:
        return jsonify({
            "enabled": robot.color_detection_enabled,
            "detected_colors": robot.get_detected_colors()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------Color Detection WebSocket Events-------------------------
@socketio.on('toggle_color_detection')
def handle_toggle_color_detection(data):
    """Active/désactive la détection de couleur via WebSocket"""
    enabled = data.get('enabled', True)
    robot.enable_color_detection(enabled)
    emit('color_detection_status', {
        'enabled': enabled,
        'message': f"Détection de couleur {'activée' if enabled else 'désactivée'}"
    }, broadcast=True)

@socketio.on('get_detected_colors')
def handle_get_detected_colors():
    """Retourne les couleurs actuellement détectées"""
    colors = robot.get_detected_colors()
    emit('detected_colors', {
        'colors': colors,
        'count': len(colors)
    })

def color_detection_thread():
    """Thread pour diffuser les couleurs détectées en temps réel"""
    import time
    while True:
        try:
            if robot and robot.color_detection_enabled:
                colors = robot.get_detected_colors()
                if colors:
                    socketio.emit('detected_colors_update', {
                        'colors': colors,
                        'timestamp': time.time()
                    })
            time.sleep(0.5)  # Diffuser toutes les 500ms
        except Exception as e:
            print(f"Erreur dans le thread de détection couleur: {e}")
            time.sleep(1)



# Démarrer le thread de détection de couleur seulement s'il n'existe pas déjà
if not hasattr(color_detection_thread, '_started'):
    color_detection_thread._started = True
    threading.Thread(target=color_detection_thread, daemon=True).start()

# ---------------Radar Scan WebSocket Events-------------------------
@socketio.on('start_radar_scan')
def handle_start_radar_scan(data):
    """Démarre un scan radar et diffuse les résultats"""
    try:
        if robot is None:
            emit('error', {"error": "Robot not initialized"})
            return
        
        # Paramètres du scan (avec valeurs par défaut)
        min_angle = data.get('min_angle', 0)
        max_angle = data.get('max_angle', 180)
        step = data.get('step', 5)
        
        # Lancer le scan radar
        from robot.radar_scan_utils import radar_scan
        scan_result = radar_scan(robot, min_angle, max_angle)
        
        # Préparer les données pour le frontend
        radar_data = {
            'angles': [],
            'distances': [],
            'min_angle': scan_result.min_angle,
            'max_angle': scan_result.max_angle,
            'timestamp': time.time()
        }
        
        # Convertir les données en format utilisable par le frontend
        angle_step = (scan_result.max_angle - scan_result.min_angle) / len(scan_result.array_result)
        for i, distance in enumerate(scan_result.array_result):
            angle = scan_result.min_angle + i * angle_step
            radar_data['angles'].append(angle)
            radar_data['distances'].append(distance)
        
        # Envoyer les données au frontend
        emit('radar_scan_result', radar_data, broadcast=True)
        
    except Exception as e:
        emit('error', {"error": f"Radar scan failed: {str(e)}"})

@socketio.on('get_radar_status')
def handle_get_radar_status():
    """Retourne l'état actuel du radar"""
    try:
        if robot is None:
            emit('error', {"error": "Robot not initialized"})
            return
        
        status = {
            'pan_angle': robot.pan_servo.current_angle,
            'tilt_angle': robot.tilt_servo.current_angle,
            'distance': robot.ultra.get_distance_cm(),
            'timestamp': time.time()
        }
        emit('radar_status', status)
    except Exception as e:
        emit('error', {"error": str(e)})
