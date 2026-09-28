from app.repositories import reservas_repository, socios_repository, canchas_repository
from app.errors import ApiError
from app.utils.datetime_utils import parsear_fecha_hora, ahora_gmt3

HORA_APERTURA = 8
HORA_CIERRE = 23
DURACION_MINIMA_HORAS = 1
DURACION_MAXIMA_HORAS = 3
ESTADOS_VALIDOS = ("confirmada", "cancelada", "finalizada")

def _validar_horario(inicio, fin):
    if inicio.minute != 0 or inicio.second != 0 or inicio.microsecond != 0:
        raise ApiError(400, "HORARIO_INVALIDO", "fecha_hora_inicio debe ser en punto (minutos y segundos en 0)")
    if fin.minute != 0 or fin.second != 0 or fin.microsecond != 0:
        raise ApiError(400, "HORARIO_INVALIDO", "fecha_hora_fin debe ser en punto (minutos y segundos en 0)")

    if fin <= inicio:
        raise ApiError(400, "RANGO_INVALIDO", "fecha_hora_fin debe ser posterior a fecha_hora_inicio")

    duracion_horas = (fin - inicio).total_seconds() / 3600
    if duracion_horas < DURACION_MINIMA_HORAS or duracion_horas > DURACION_MAXIMA_HORAS:
        raise ApiError(400, "DURACION_INVALIDA", "La reserva debe durar entre 1 y 3 horas")

    if inicio.date() != fin.date():
        raise ApiError(400, "RANGO_INVALIDO", "La reserva no puede cruzar la medianoche")

    if inicio.hour < HORA_APERTURA or fin.hour > HORA_CIERRE:
        raise ApiError(400, "FUERA_DE_HORARIO", f"El club atiende de {HORA_APERTURA}:00 a {HORA_CIERRE}:00")

    if inicio <= ahora_gmt3():
        raise ApiError(400, "FECHA_PASADA", "La reserva debe ser en el futuro")


def crear_reserva(data):
    id_socio = data.get("id_socio")
    id_cancha = data.get("id_cancha")

    if not isinstance(id_socio, int) or isinstance(id_socio, bool):
        raise ApiError(400, "ID_SOCIO_INVALIDO", "id_socio debe ser un número entero")
    if not isinstance(id_cancha, int) or isinstance(id_cancha, bool):
        raise ApiError(400, "ID_CANCHA_INVALIDO", "id_cancha debe ser un número entero")

    inicio = parsear_fecha_hora(data.get("fecha_hora_inicio"))
    fin = parsear_fecha_hora(data.get("fecha_hora_fin"))

    if inicio is None:
        raise ApiError(400, "FECHA_INICIO_INVALIDA", "fecha_hora_inicio no tiene el formato esperado")
    if fin is None:
        raise ApiError(400, "FECHA_FIN_INVALIDA", "fecha_hora_fin no tiene el formato esperado")

    _validar_horario(inicio, fin)

    socio = socios_repository.find_by_id(id_socio)
    if socio is None:
        raise ApiError(404, "SOCIO_NO_ENCONTRADO", "No existe un socio con ese id")
    if not socio["activo"]:
        raise ApiError(409, "SOCIO_INACTIVO", "El socio no puede realizar reservas")

    cancha = canchas_repository.find_by_id(id_cancha)
    if cancha is None:
        raise ApiError(404, "CANCHA_NO_ENCONTRADA", "No existe una cancha con ese id")
    if not cancha["activa"]:
        raise ApiError(409, "CANCHA_INACTIVA", "La cancha no admite nuevas reservas")

    if reservas_repository.existe_solapamiento_cancha(id_cancha, inicio, fin):
        raise ApiError(409, "CANCHA_NO_DISPONIBLE", "La cancha ya tiene una reserva confirmada en ese horario")
    if reservas_repository.existe_solapamiento_socio(id_socio, inicio, fin):
        raise ApiError(409, "SOCIO_CON_SOLAPAMIENTO", "El socio ya tiene una reserva confirmada en ese horario")

    horas = int((fin - inicio).total_seconds() // 3600)
    precio_hora = cancha["precio_hora"]
    precio_total = horas * precio_hora

    nuevo_id = reservas_repository.insert(id_socio, id_cancha, inicio, fin, precio_hora, precio_total)
    return reservas_repository.find_by_id(nuevo_id)


def listar_reservas(id_cancha, id_socio, estado, fecha_desde, fecha_hasta, limit, offset):
    reservas = reservas_repository.find_all(id_cancha, id_socio, estado, fecha_desde, fecha_hasta, limit, offset)
    total = reservas_repository.count(id_cancha, id_socio, estado, fecha_desde, fecha_hasta)
    return reservas, total


def obtener_reserva(id_reserva):
    reserva = reservas_repository.find_by_id(id_reserva)
    if reserva is None:
        raise ApiError(404, "RESERVA_NO_ENCONTRADA", "No existe una reserva con ese id")
    return reserva


def cambiar_estado(id_reserva, data):
    reserva = obtener_reserva(id_reserva)
    nuevo_estado = data.get("estado")

    if nuevo_estado not in ESTADOS_VALIDOS:
        raise ApiError(400, "ESTADO_INVALIDO", "estado debe ser confirmada, cancelada o finalizada")

    estado_actual = reserva["estado"]

    if nuevo_estado == estado_actual:
        return reserva

    if estado_actual != "confirmada":
        raise ApiError(409, "TRANSICION_INVALIDA", "La reserva ya no admite cambios de estado")

    ahora = ahora_gmt3()
    inicio = parsear_fecha_hora(reserva["fecha_hora_inicio"])
    fin = parsear_fecha_hora(reserva["fecha_hora_fin"])

    if nuevo_estado == "cancelada":
        if ahora >= inicio:
            raise ApiError(409, "TRANSICION_INVALIDA", "No se puede cancelar una reserva que ya comenzó")
    elif nuevo_estado == "finalizada":
        if ahora < fin:
            raise ApiError(409, "TRANSICION_INVALIDA", "No se puede finalizar una reserva que todavía no terminó")

    reservas_repository.actualizar_estado(id_reserva, nuevo_estado)
    return reservas_repository.find_by_id(id_reserva)