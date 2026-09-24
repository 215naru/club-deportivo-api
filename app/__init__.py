from flask import Flask, jsonify
from app.config import Config
from app import db
from app.errors import ApiError
from app.routes.socios import socios_bp

def create_app():
    app = Flask(__name__)
    app.config["APP_CONFIG"] = Config()

    db.init_app(app)

    app.register_blueprint(socios_bp)

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({"errors":[{"code":error.code, "message":error.message}]}), error.status_code


    return app