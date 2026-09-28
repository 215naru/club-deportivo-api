from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
import mysql.connector
from app.config import Config
from app import db
from app.errors import ApiError
from app.routes.socios import socios_bp
from app.routes.canchas import canchas_bp
from app.routes.reservas import reservas_bp
from app.routes.deportes import deportes_bp


def _error(status, code, message):
    return jsonify({"errors": [{
        "code": code, "message": message,
        "level": "error", "description": message
    }]}), status


def create_app():
    app = Flask(__name__)
    app.config["APP_CONFIG"] = Config()
    app.json.ensure_ascii = False   # tildes legibles en las respuestas

    db.init_app(app)

    app.register_blueprint(socios_bp)
    app.register_blueprint(canchas_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(deportes_bp)

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return _error(error.status_code, error.code, error.message)

    @app.errorhandler(HTTPException)          # 404, 405, etc.
    def handle_http_error(error):
        return _error(error.code, error.name.upper().replace(" ", "_"), error.description)

    @app.errorhandler(mysql.connector.IntegrityError)
    def handle_integrity_error(error):
        if error.errno == 1062:               # UNIQUE (ej.: email duplicado en carrera)
            return _error(409, "REGISTRO_DUPLICADO", "Ya existe un registro con ese valor")
        if error.errno in (1451, 1452):       # FK (ej.: borrar cancha con reservas en carrera)
            return _error(409, "VIOLACION_INTEGRIDAD", "La operación viola una restricción de integridad")
        return _error(500, "ERROR_INTERNO", "Error interno del servidor")

    @app.errorhandler(Exception)              # cualquier otra cosa: 500 sin filtrar detalles
    def handle_unexpected_error(error):
        app.logger.exception(error)
        return _error(500, "ERROR_INTERNO", "Error interno del servidor")

    return app