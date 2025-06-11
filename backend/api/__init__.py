from flask import Flask
from flask_cors import CORS
from .routes import robot_routes , set_robot_instance
from flasgger import Swagger

def create_app(robot=None):
    
    app = Flask(__name__)
    # Pendant le dev, on ouvre tout
    CORS(app, resources={r"/*": {"origins": "*"}})
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

