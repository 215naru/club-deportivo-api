from flask import jsonify, Blueprint, request
from app.services import socios_service
from app.utils.pagination import obtener_paginacion, construir_links

socios_bp = Blueprint("socios",__name__)

@socios_bp.route("/socios", methods=["GET"])
def listar_socio():
    limit, offset = obtener_paginacion(request.args)
    socios, total = socios_service.listar_socios(limit, offset)

    if not socios:
        return "", 204
    
    links = construir_links(request.base_url,limit,offset,total)
    return jsonify({"socios":socios,"_links":links}), 200

@socios_bp.route("/socios", methods=["POST"])
def crear_socio():
    data = request.get_json(silent=True) or {}
    socio = socios_service.crear_socio(data)
    return jsonify(socio), 201

@socios_bp.route("/socios/<int:id_socio>", methods=["GET"])
def obtener_socio(id_socio):
    socio = socios_service.obtener_socio(id_socio)
    return jsonify(socio), 200

@socios_bp.route("/socios/<int:id_socio>", methods=["PATCH"])
def actualizar_socio(id_socio):
    data = request.get_json(silent=True) or {}
    socios_service.actualizar_socio(id_socio, data)
    return "",204