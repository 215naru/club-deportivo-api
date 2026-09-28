from flask import Blueprint, jsonify, request
from app.services import canchas_service
from app.utils.pagination import obtener_paginacion, construir_links, validar_parametros_conocidos
from app.errors import ApiError

canchas_bp = Blueprint("canchas",__name__)

def _parametro_entero(nombre):
    valor = request.args.get(nombre)
    if valor is None:
        return None
    try:
        return int(valor)
    except ValueError:
        raise ApiError(400, "FILTRO_INVALIDO", f"{nombre} debe ser un número entero")

def _parametro_booleano(nombre):
    valor = request.args.get(nombre)
    if valor is None:
        return None
    if valor == "true":
        return True
    if valor == "false":
        return False
    raise ApiError(400, "FILTRO_INVALIDO", f"{nombre} debe ser true o false")

@canchas_bp.route("/canchas", methods=["POST"])
def crear_cancha():
    data = request.get_json(silent=True) or {}
    cancha = canchas_service.crear_cancha(data)
    return jsonify(cancha), 201

@canchas_bp.route("/canchas", methods=["GET"])
def listar_canchas():
    validar_parametros_conocidos(request.args, {"_limit", "_offset", "id_deporte", "nombre", "techada", "activa"})
    limit, offset = obtener_paginacion(request.args)

    id_deporte = _parametro_entero("id_deporte")
    nombre = request.args.get("nombre")
    techada = _parametro_booleano("techada")
    activa = _parametro_booleano("activa")

    canchas, total = canchas_service.listar_canchas(limit, offset, id_deporte, nombre, techada, activa)

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

@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def canchas_disponibles():
    validar_parametros_conocidos(
        request.args,
        {"_limit", "_offset", "fecha", "hora_inicio", "hora_fin", "id_deporte", "techada"}
    )
    limit, offset = obtener_paginacion(request.args)

    fecha = request.args.get("fecha")
    hora_inicio = request.args.get("hora_inicio")
    hora_fin = request.args.get("hora_fin")

    if fecha is None or hora_inicio is None or hora_fin is None:
        raise ApiError(400, "PARAMETRO_REQUERIDO", "fecha, hora_inicio y hora_fin son obligatorios")

    id_deporte = _parametro_entero("id_deporte")
    techada = _parametro_booleano("techada")

    canchas, total = canchas_service.consultar_disponibles(
        fecha, hora_inicio, hora_fin, id_deporte, techada, limit, offset
    )

    if not canchas:
        return "", 204

    links = construir_links(request.base_url, limit, offset, total)
    return jsonify({"canchas": canchas, "_links": links}), 200