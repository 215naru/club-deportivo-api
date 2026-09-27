from flask import Blueprint, jsonify, request
from app.services import canchas_service
from app.utils.pagination import obtener_paginacion, construir_links

canchas_bp = Blueprint("canchas",__name__)

@canchas_bp.route("/canchas", methods=["POST"])
def crear_cancha():
    data = request.get_json(silent=True) or {}
    cancha = canchas_service.crear_cancha(data)
    return jsonify(cancha), 201

@canchas_bp.route("/canchas", methods=["GET"])
def listar_canchas():
    limit, offset = obtener_pagincion(request.args)
    canchas, total = canchas_service.listar_canchas(limit, offset)

    if not canchas:
        return "", 204
    
    links = construir_links(request.base_url, limit, offset, total)
    return jsonify({
        "canchas": canchas,
        "_links": links
    }), 200

@canchas_bp.route("/canchas/<int:id_cancha>", methods=["GET"])
def obtener_cancha(id_cancha):
    cancha = canchas_service.obtener_cancha(id_cancha)
    return jsonify(cancha), 200

@canchas_bp.route("/canchas/<int:id_cancha>", methods=["PATCH"])
def actualizar_cancha(id_cancha):
    data = request.get_json(silent=True) or {}
    canchas_service.actualizar_cancha(id_cancha, data)
    return "", 204

@canchas_bp.route("/canchas/<int:id_cancha>", methods=["DELETE"])
def eliminar_cancha(id_cancha):
    canchas_service.eliminar_cancha(id_cancha)
    return "", 204