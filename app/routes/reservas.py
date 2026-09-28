from flask import Blueprint, jsonify, request
from app.services import reservas_service
from app.utils.pagination import obtener_paginacion, construir_links

reservas_bp = Blueprint("reservas", __name__)

@reservas_bp.route("/reservas", methods=["GET"])
def listar_reservas():
    limit, offset = obtener_paginacion(request.args)
    reservas, total = reservas_service.listar_reservas(limit, offset, request.args)

    if not reservas:
        return "", 204

    links = construir_links(request.base_url, limit, offset, total)
    return jsonify({"reservas": reservas, "_links": links}), 200

@reservas_bp.route("/reservas", methods=["POST"])
def crear_reserva():
    data = request.get_json(silent=True) or {}
    reserva = reservas_service.crear_reserva(data)
    return jsonify(reserva), 201

@reservas_bp.route("/reservas/<int:id_reserva>", methods=["GET"])
def obtener_reserva(id_reserva):
    reserva = reservas_service.obtener_reserva(id_reserva)
    return jsonify(reserva), 200

@reservas_bp.route("/reservas/<int:id_reserva>/estado", methods=["PUT"])
def cambiar_estado(id_reserva):
    data = request.get_json(silent=True) or {}
    reservas_service.cambiar_estado(id_reserva, data)
    return "", 204
