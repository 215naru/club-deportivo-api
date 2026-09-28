import re
from datetime import datetime, time, timedelta, timezone
from app.repositories import reservas_repository
from app.repositories import socios_repository
from app.repositories import canchas_repository
from app.errors import ApiError

# CONSTANTES

ESTADOS_VALIDOS = {"confirmada","cancelada","finalizada"}
CAMPOS_RESERVA_CREATE = {"id_socio","id_cancha","fecha_hora_inicio","fecha_hora_fin"}
CAMPOS_ESTADO = {"estado"}
HORA_APERTURA = time(8, 0, 0)
HORA_CIERRE = time(23, 0, 0)
GMT_MENOS_3 = timezone(timedelta(hours=-3))
FECHA_HORA_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}"r"T\d{2}:\d{2}:\d{2}\."r"\d{6}-03:00$")
FECHA_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# VALIDACIONES GENERALES

def _validar_entero_positivo(valor, nombre):
    if (not isinstance(valor, int)or isinstance(valor, bool)or valor <= 0):
        raise ApiError(400,f"{nombre.upper()}_INVALIDO",f"{nombre} debe ser un entero positivo")

def _parsear_fecha_hora(valor, nombre):
    """
    Valida el formato exacto exigido por Swagger:
    YYYY-MM-DDTHH:MM:SS.ffffff-03:00
    """
    if not isinstance(valor, str):
        raise ApiError(400,"FECHA_HORA_INVALIDA",f"{nombre} debe ser una cadena de fecha/hora")
    if not FECHA_HORA_PATTERN.fullmatch(valor):
        raise ApiError(400,"FECHA_HORA_INVALIDA",(f"{nombre} debe respetar el formato ""YYYY-MM-DDTHH:MM:SS.ffffff-03:00"))
    try:
        fecha_hora = datetime.strptime(valor,"%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        raise ApiError(400,"FECHA_HORA_INVALIDA",f"{nombre} no representa una fecha/hora válida")
    if fecha_hora.utcoffset() != timedelta(hours=-3):
        raise ApiError(400,"FECHA_HORA_INVALIDA",f"{nombre} debe utilizar GMT-3")
    return fecha_hora.replace(tzinfo=None)

def _parsear_fecha(valor, nombre):
    if (not isinstance(valor, str) or not FECHA_PATTERN.fullmatch(valor)):
        raise ApiError(400,"FECHA_INVALIDA",f"{nombre} debe tener formato YYYY-MM-DD")
    try:
        return datetime.strptime(valor,"%Y-%m-%d").date()
    except ValueError:
        raise ApiError(400,"FECHA_INVALIDA",f"{nombre} no representa una fecha válida")

# VALIDACION DEL BODY

def _validar_body_creacion(data):
    if not isinstance(data, dict):
        raise ApiError(400,"CUERPO_INVALIDO","El cuerpo debe ser un objeto JSON")
    desconocidos = set(data.keys()) - CAMPOS_RESERVA_CREATE
    if desconocidos:
        raise ApiError(400,"CAMPO_DESCONOCIDO",("El cuerpo contiene campos desconocidos: "+ ", ".join(sorted(desconocidos))))
    faltantes = CAMPOS_RESERVA_CREATE - set(data.keys())
    if faltantes:
        raise ApiError(400,"CAMPO_REQUERIDO",("Faltan campos obligatorios: "+ ", ".join(sorted(faltantes))))

def _validar_body_estado(data):
    if not isinstance(data, dict):
        raise ApiError(400,"CUERPO_INVALIDO","El cuerpo debe ser un objeto JSON")
    desconocidos = set(data.keys()) - CAMPOS_ESTADO
    if desconocidos:
        raise ApiError(400,"CAMPO_DESCONOCIDO",("El cuerpo contiene campos desconocidos: "+ ", ".join(sorted(desconocidos))))
    if "estado" not in data:
        raise ApiError(400,"ESTADO_REQUERIDO","El campo estado es obligatorio")

# VALIDACIONES DE INTERVALO

def _validar_intervalo(inicio, fin):
    if inicio >= fin:
        raise ApiError(400,"INTERVALO_INVALIDO","La fecha_hora_inicio debe ser anterior a fecha_hora_fin")
    if inicio.date() != fin.date():
        raise ApiError(400,"INTERVALO_INVALIDO","La reserva no puede atravesar la medianoche")
    if (inicio.minute != 0 or inicio.second != 0 or inicio.microsecond != 0):
        raise ApiError(400,"HORARIO_INVALIDO","La reserva debe comenzar en una hora exacta")
    if (fin.minute != 0 or fin.second != 0 or fin.microsecond != 0):
        raise ApiError(400,"HORARIO_INVALIDO","La reserva debe finalizar en una hora exacta")
    if inicio.time() < HORA_APERTURA:
        raise ApiError(400,"HORARIO_INVALIDO","La reserva no puede comenzar antes de las 08:00")
    if fin.time() > HORA_CIERRE:
        raise ApiError(400,"HORARIO_INVALIDO","La reserva no puede finalizar después de las 23:00")
    duracion = fin - inicio
    duraciones_validas = {timedelta(hours=1),timedelta(hours=2),timedelta(hours=3)}
    if duracion not in duraciones_validas:
        raise ApiError(400,"DURACION_INVALIDA","La reserva debe durar una, dos o tres horas")

def _validar_reserva_futura(inicio):
    """
    El inicio debe ser estrictamente posterior
    al momento actual.
    Interpretamos ambos valores en GMT-3 fijo.
    """
    ahora = datetime.now(GMT_MENOS_3).replace(tzinfo=None)
    if inicio <= ahora:
        raise ApiError(400,"RESERVA_NO_FUTURA","La reserva debe comenzar en un momento posterior al actual")

# SERIALIZACION

def _reserva_a_json(reserva):
    if reserva is None:
        return None
    resultado = dict(reserva)
    for campo in ("fecha_hora_inicio","fecha_hora_fin"):
        valor = resultado.get(campo)
        if isinstance(valor, datetime):
            resultado[campo] = valor.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")
    return resultado

# GET /reservas

def listar_reservas(limit, offset, filtros):
    id_cancha = None
    id_socio = None
    estado = None
    fecha_desde = None
    fecha_hasta = None
    if "id_cancha" in filtros:
        try:
            id_cancha = int(filtros["id_cancha"])
        except (TypeError, ValueError):
            raise ApiError(400,"ID_CANCHA_INVALIDO","id_cancha debe ser un entero positivo")
        _validar_entero_positivo(id_cancha,"id_cancha")
    if "id_socio" in filtros:
        try:
            id_socio = int(filtros["id_socio"])
        except (TypeError, ValueError):
            raise ApiError(400,"ID_SOCIO_INVALIDO","id_socio debe ser un entero positivo")
        _validar_entero_positivo(id_socio,"id_socio")
    if "estado" in filtros:
        estado = filtros["estado"]
        if estado not in ESTADOS_VALIDOS:
            raise ApiError(400,"ESTADO_INVALIDO","estado debe ser confirmada, cancelada o finalizada")
    if "fecha_desde" in filtros:
        fecha_desde = _parsear_fecha(filtros["fecha_desde"],"fecha_desde")
    if "fecha_hasta" in filtros:
        fecha_hasta = _parsear_fecha(filtros["fecha_hasta"],"fecha_hasta")
    if (fecha_desde is not None and fecha_hasta is not None and fecha_desde > fecha_hasta):
        raise ApiError(400,"RANGO_FECHAS_INVALIDO","fecha_desde debe ser menor o igual a fecha_hasta")
    reservas = reservas_repository.find_all(limit=limit,offset=offset,id_cancha=id_cancha,id_socio=id_socio,estado=estado,fecha_desde=fecha_desde,fecha_hasta=fecha_hasta)
    total = reservas_repository.count(id_cancha=id_cancha,id_socio=id_socio,estado=estado,fecha_desde=fecha_desde,fecha_hasta=fecha_hasta)
    reservas = [_reserva_a_json(reserva) for reserva in reservas]
    return reservas, total

# POST /reservas

def crear_reserva(data):
    _validar_body_creacion(data)
    _validar_entero_positivo(data["id_socio"],"id_socio")
    _validar_entero_positivo(data["id_cancha"],"id_cancha")
    socio = socios_repository.find_by_id(data["id_socio"])
    if socio is None:
        raise ApiError(404,"SOCIO_NO_ENCONTRADO","No existe un socio con ese id")
    if not socio["activo"]:
        raise ApiError(409,"SOCIO_INACTIVO","El socio no está activo")
    cancha = canchas_repository.find_by_id(data["id_cancha"])
    if cancha is None:
        raise ApiError(404,"CANCHA_NO_ENCONTRADA","No existe una cancha con ese id")
    if not cancha["activa"]:
        raise ApiError(409,"CANCHA_INACTIVA","La cancha no está activa")
    inicio = _parsear_fecha_hora(data["fecha_hora_inicio"],"fecha_hora_inicio")
    fin = _parsear_fecha_hora(data["fecha_hora_fin"],"fecha_hora_fin")
    _validar_intervalo(inicio,fin)
    _validar_reserva_futura(inicio)
    conflicto_cancha = reservas_repository.find_conflict_cancha(id_cancha=data["id_cancha"],fecha_hora_inicio=inicio,fecha_hora_fin=fin)
    if conflicto_cancha is not None:
        raise ApiError(409,"CANCHA_NO_DISPONIBLE","La cancha ya tiene una reserva confirmada superpuesta")
    conflicto_socio = reservas_repository.find_conflict_socio(id_socio=data["id_socio"],fecha_hora_inicio=inicio,fecha_hora_fin=fin)
    if conflicto_socio is not None:
        raise ApiError(409,"SOCIO_NO_DISPONIBLE","El socio ya tiene una reserva confirmada superpuesta")
    horas = int((fin - inicio).total_seconds() / 3600)
    precio_hora = cancha["precio_hora"]
    precio_total = precio_hora * horas
    nuevo_id = reservas_repository.insert(id_socio=data["id_socio"],id_cancha=data["id_cancha"],fecha_hora_inicio=inicio,fecha_hora_fin=fin,estado="confirmada",precio_hora=precio_hora,precio_total=precio_total)
    return obtener_reserva(nuevo_id)

# GET /reservas/{id}

def obtener_reserva(id_reserva):
    _validar_entero_positivo(id_reserva,"id_reserva")
    reserva = reservas_repository.find_by_id(id_reserva)
    if reserva is None:
        raise ApiError(404,"RESERVA_NO_ENCONTRADA","No existe una reserva con ese id")
    return _reserva_a_json(reserva)

# PUT /reservas/{id}/estado

def cambiar_estado(id_reserva, data):
    _validar_entero_positivo(id_reserva,"id_reserva")
    _validar_body_estado(data)
    nuevo_estado = data["estado"]
    if not isinstance(nuevo_estado, str):
        raise ApiError(400,"ESTADO_INVALIDO","El estado debe ser un texto")
    if nuevo_estado not in ESTADOS_VALIDOS:
        raise ApiError(400,"ESTADO_INVALIDO","Estado desconocido")
    reserva = reservas_repository.find_by_id(id_reserva)
    if reserva is None:
        raise ApiError(404,"RESERVA_NO_ENCONTRADA","No existe una reserva con ese id")
    estado_actual = reserva["estado"]
    if estado_actual == nuevo_estado:
        return
    if estado_actual == "cancelada":
        raise ApiError(409,"TRANSICION_INVALIDA","Una reserva cancelada no puede cambiar de estado")
    if estado_actual == "finalizada":
        raise ApiError(409,"TRANSICION_INVALIDA","Una reserva finalizada no puede cambiar de estado")
    if (estado_actual == "confirmada" and nuevo_estado == "cancelada"):
        ahora = datetime.now(GMT_MENOS_3).replace(tzinfo=None)
        if ahora >= reserva["fecha_hora_inicio"]:
            raise ApiError(409,"CANCELACION_NO_PERMITIDA",("No se puede cancelar una reserva cuyo inicio ya llegó"))
        reservas_repository.update_estado(id_reserva,"cancelada")
        return
    if (estado_actual == "confirmada" and nuevo_estado == "finalizada"):
        ahora = datetime.now(GMT_MENOS_3).replace(tzinfo=None)
        if ahora < reserva["fecha_hora_fin"]:
            raise ApiError(409,"FINALIZACION_NO_PERMITIDA",("La reserva todavía no alcanzó su horario de finalización"))
        reservas_repository.update_estado(id_reserva,"finalizada")
        return
    raise ApiError(409,"TRANSICION_INVALIDA",(f"No se permite cambiar una reserva " f"de {estado_actual} a {nuevo_estado}"))
