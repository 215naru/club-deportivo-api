from flask import Blueprint, jsonify, request
from app.services import deportes_service
from app.utils.pagination import validar_parametros_conocidos

deportes_bp = Blueprint("deportes", __name__)

@deportes_bp.route("/deportes", methods=["GET"])
def listar_deportes():
    validar_parametros_conocidos(request.args, set())
    deportes = deportes_service.listar_deportes()

    if not deportes:
        return "", 204

    return jsonify({"deportes": deportes}), 200
