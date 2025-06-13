from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def create_app(robot=None):
    
    from .routes import robot_routes , set_robot_instance
    CORS(app)
    set_robot_instance(robot)
    # Enregistrement de tes routes
    app.register_blueprint(robot_routes)
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Robot Motor API",
            "description": "API for controlling the robot's motors",
            "version": "1.0.0"
        }
    })

    return app

