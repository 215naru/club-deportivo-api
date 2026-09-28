from flask import jsonify, Blueprint, request
from app.services import socios_service
from app.utils.pagination import obtener_paginacion, construir_links, validar_parametros_conocidos
from app.errors import ApiError

socios_bp = Blueprint("socios",__name__)

def _parametro_booleano(nombre):
    valor = request.args.get(nombre)
    if valor is None:
        return None
    if valor == "true":
        return True
    if valor == "false":
        return False
    raise ApiError(400, "FILTRO_INVALIDO", f"{nombre} debe ser true o false")

@socios_bp.route("/socios", methods=["GET"])
def listar_socio():
    validar_parametros_conocidos(request.args, {"_limit", "_offset", "nombre", "activo"})
    limit, offset = obtener_paginacion(request.args)
    nombre = request.args.get("nombre")
    activo = _parametro_booleano("activo")
    socios, total = socios_service.listar_socios(limit, offset, nombre, activo)

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