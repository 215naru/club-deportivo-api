from urllib.parse import urlencode
from flask import Blueprint, jsonify, request
from app.errors import ApiError
from app.services import reservas_service
from app.utils.pagination import obtener_paginacion

reservas_bp = Blueprint("reservas",__name__)

FILTROS_PERMITIDOS = {"id_cancha","id_socio","estado","fecha_desde","fecha_hasta"}

def _construir_links(base_url,filtros,limit,offset,total):
    """
    Construye los links HATEOAS para /reservas.
    Se hace acá y no se reutiliza construir_links()
    porque la implementación actual de pagination.py
    tiene un problema en algunos query strings.
    """
    def construir_url(nuevo_offset):
        parametros = dict(filtros)
        parametros["_limit"] = limit
        parametros["_offset"] = nuevo_offset
        return (f"{base_url}?"f"{urlencode(parametros)}")
    links = {"_first": {"href": construir_url(0)}}

    if offset > 0:
        anterior = max(offset - limit,0)
        links["_prev"] = {"href": construir_url(anterior)}
    siguiente = offset + limit

    if siguiente < total:
        links["_next"] = {"href": construir_url(siguiente)}

    if total > 0:
        ultimo = ((total - 1) // limit) * limit
        links["_last"] = {"href": construir_url(ultimo)}
    return links

# GET /reservas

@reservas_bp.route("/reservas",methods=["GET"])

def listar_reservas():
    limit, offset = obtener_paginacion(request.args)
    parametros_permitidos = (FILTROS_PERMITIDOS| {"_limit", "_offset"})
    desconocidos = [parametro for parametro in request.args.keys()if parametro not in parametros_permitidos]
    if desconocidos:
        raise ApiError(400,"PARAMETRO_DESCONOCIDO",("Parámetro(s) desconocido(s): "+ ", ".join(desconocidos)))
    filtros = {}
    for filtro in FILTROS_PERMITIDOS:
        if filtro in request.args:
            filtros[filtro] = request.args.get(filtro)
    reservas, total = reservas_service.listar_reservas(limit,offset,filtros)
    # El Swagger contempla 204 cuando no hay contenido
    if not reservas:
        return "", 204
    links = _construir_links(request.base_url,filtros,limit,offset,total)
    return jsonify({"reservas": reservas,"_links": links}), 200

# POST /reservas

@reservas_bp.route("/reservas",methods=["POST"])
def crear_reserva():
    data = request.get_json(silent=True)
    if data is None:
        raise ApiError(400,"CUERPO_INVALIDO","El cuerpo de la solicitud debe ser un objeto JSON")
    reserva = reservas_service.crear_reserva(data)
    return "", 201

# GET /reservas/{id}

@reservas_bp.route("/reservas/<int:id_reserva>",methods=["GET"])
def obtener_reserva(id_reserva):
    reserva = reservas_service.obtener_reserva(id_reserva)
    return jsonify(reserva), 200

# PUT /reservas/{id}/estado

@reservas_bp.route("/reservas/<int:id_reserva>/estado",methods=["PUT"])
def cambiar_estado(id_reserva):
    data = request.get_json(silent=True)
    if data is None:
        raise ApiError(400,"CUERPO_INVALIDO","El cuerpo de la solicitud debe ser un objeto JSON")
    reservas_service.cambiar_estado(id_reserva,data)
    return "", 204
