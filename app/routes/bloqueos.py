from flask import Blueprint, jsonify, request
from app.services import bloqueos_service
from app.utils.pagination import obtener_paginacion, construir_links

bloqueos_bp = Blueprint("bloqueos", __name__)

@bloqueos_bp.route("/bloqueos", methods=["POST"])
def crear_bloqueo():
    data = request.get_json(silent=True) or {}
    bloqueo = bloqueos_service.crear_bloqueo(data)
    return jsonify(bloqueo), 201

@bloqueos_bp.route("/bloqueos", methods=["GET"])
def listar_bloqueos():
    limit, offset = obtener_paginacion(request.args)
    id_cancha = request.args.get("id_cancha", type=int)
    fecha = request.args.get("fecha")
    bloqueos, total = bloqueos_service.listar_bloqueos(limit, offset, id_cancha, fecha)

    if not bloqueos:
        return "", 204

    links = construir_links(request.base_url, limit, offset, total)
    return jsonify({"bloqueos": bloqueos, "_links": links}), 200

@bloqueos_bp.route("/bloqueos/<int:id_bloqueo>", methods=["DELETE"])
def eliminar_bloqueo(id_bloqueo):
    bloqueos_service.eliminar_bloqueo(id_bloqueo)
    return "", 204
