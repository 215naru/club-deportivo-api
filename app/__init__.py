from flask import Flask
from app.config import Config
from app import db

def create_app():
    app = Flask(__name__)
    app.config["APP_CONFIG"] = Config()

    db.init_app(app)
    return app