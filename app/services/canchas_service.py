import re
from datetime import datetime, timedelta, timezone
from app.repositories import canchas_repository
from app.errors import ApiError

FECHA_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HORA_PATTERN = re.compile(r"^([01]\d|2[0-3]):00:00$")
HORA_APERTURA = "08:00:00"
HORA_CIERRE = "23:00:00"
GMT_MENOS_3 = timezone(timedelta(hours=-3))
DURACIONES_VALIDAS = {timedelta(hours=1), timedelta(hours=2), timedelta(hours=3)}
CAMPOS_CANCHA_CREATE = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
CAMPOS_CANCHA_REQUERIDOS = {"nombre", "id_deporte", "precio_hora"}
CAMPOS_CANCHA_UPDATE = {"nombre", "precio_hora", "techada", "activa"}

def _validar_body_creacion(data):
    if not isinstance(data, dict):
        raise ApiError(400, "CUERPO_INVALIDO", "El cuerpo debe ser un objeto JSON")
    desconocidos = set(data.keys()) - CAMPOS_CANCHA_CREATE
    if desconocidos:
        raise ApiError(400, "CAMPO_DESCONOCIDO", "El cuerpo contiene campos desconocidos: " + ", ".join(sorted(desconocidos)))
    faltantes = CAMPOS_CANCHA_REQUERIDOS - set(data.keys())
    if faltantes:
        raise ApiError(400, "CAMPO_REQUERIDO", "Faltan campos obligatorios: " + ", ".join(sorted(faltantes)))

def _validar_body_actualizacion(data):
    if not isinstance(data, dict):
        raise ApiError(400, "CUERPO_INVALIDO", "El cuerpo debe ser un objeto JSON")
    if not data:
        raise ApiError(400, "CUERPO_VACIO", "El cuerpo no puede estar vacío")
    desconocidos = set(data.keys()) - CAMPOS_CANCHA_UPDATE
    if desconocidos:
        raise ApiError(400, "CAMPO_DESCONOCIDO", "El cuerpo contiene campos desconocidos: " + ", ".join(sorted(desconocidos)))

def crear_cancha(data):
    _validar_body_creacion(data)
    nombre = data.get("nombre","").strip()
    id_deporte = data.get("id_deporte")
    precio_hora = data.get("precio_hora")
    techada = data.get("techada", False)
    activa = data.get("activa", True)

    if not nombre:
        raise ApiError(400, "NOMBRE_INVALIDO", "El nombre es obligatorio")

    if not isinstance(id_deporte,int) or isinstance(id_deporte,bool):
        raise ApiError(400, "ID_DEPORTE_INVALIDO", "id_deporte debe ser un número entero")

    if not canchas_repository.existe_deporte(id_deporte):
        raise ApiError(404, "DEPORTE_NO_ENCONTRADO", "No existe un deporte con ese id")
    
    if not isinstance(precio_hora, int) or isinstance(precio_hora, bool) or precio_hora <= 0:
        raise ApiError(400, "PRECIO_INVALIDO", "precio_hora debe ser un entero mayor a cero")

    if not isinstance(techada, bool):
        raise ApiError(400, "TECHADA_INVALIDA", "techada debe ser true o false")

    if not isinstance(activa, bool):
        raise ApiError(400, "ACTIVA_INVALIDA", "activa debe ser true o false")

    nuevo_id = canchas_repository.insert(nombre, id_deporte, precio_hora, techada, activa)
    return canchas_repository.find_by_id(nuevo_id)

def listar_canchas(limit, offset, id_deporte=None, nombre=None, techada=None, activa=None):
    canchas = canchas_repository.find_all(limit, offset, id_deporte, nombre, techada, activa)
    total = canchas_repository.count(id_deporte, nombre, techada, activa)
    return canchas, total

def obtener_cancha(id_cancha):
    cancha = canchas_repository.find_by_id(id_cancha)
    if cancha is None:
        raise ApiError(404,"CANCHA_NO_ENCONTRADA","No existe una cancha con ese id")
    return cancha

def actualizar_cancha(id_cancha, data):
    cancha = obtener_cancha(id_cancha)
    _validar_body_actualizacion(data)

    nombre = data.get("nombre", cancha["nombre"]).strip()
    precio_hora = data.get("precio_hora", cancha["precio_hora"])
    techada = data.get("techada", cancha["techada"])
    activa = data.get("activa", cancha["activa"])

    if not nombre:
        raise ApiError(400, "NOMBRE_INVALIDO", "El nombre es obligatorio")

    if not isinstance(precio_hora, int) or isinstance(precio_hora, bool) or precio_hora <= 0:
        raise ApiError(400, "PRECIO_INVALIDO", "precio_hora debe ser un entero mayor a cero")

    if not isinstance(techada, bool):
        raise ApiError(400, "TECHADA_INVALIDA", "techada debe ser true o false")

    if not isinstance(activa, bool):
        raise ApiError(400, "ACTIVA_INVALIDA", "activa debe ser true o false")

    canchas_repository.update(id_cancha, nombre, precio_hora, techada, activa)
    return canchas_repository.find_by_id(id_cancha)

def eliminar_cancha(id_cancha):
    obtener_cancha(id_cancha)
    if canchas_repository.tiene_reservas(id_cancha):
        raise ApiError(409, "CANCHA_CON_RESERVAS", "No se puede eliminar una cancha con reservas asociadas")
    canchas_repository.delete(id_cancha)

def consultar_disponibles(fecha, hora_inicio, hora_fin, id_deporte, techada, limit, offset):
    if not isinstance(fecha, str) or not FECHA_PATTERN.fullmatch(fecha):
        raise ApiError(400, "FECHA_INVALIDA", "fecha debe tener formato YYYY-MM-DD")
    if not isinstance(hora_inicio, str) or not HORA_PATTERN.fullmatch(hora_inicio):
        raise ApiError(400, "HORA_INICIO_INVALIDA", "hora_inicio debe tener formato HH:00:00")
    if not isinstance(hora_fin, str) or not HORA_PATTERN.fullmatch(hora_fin):
        raise ApiError(400, "HORA_FIN_INVALIDA", "hora_fin debe tener formato HH:00:00")

    try:
        fecha_hora_inicio = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M:%S")
        fecha_hora_fin = datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ApiError(400, "FECHA_INVALIDA", "fecha no representa un día válido")

    if fecha_hora_fin <= fecha_hora_inicio:
        raise ApiError(400, "INTERVALO_INVALIDO", "hora_fin debe ser posterior a hora_inicio")
    if hora_inicio < HORA_APERTURA or hora_fin > HORA_CIERRE:
        raise ApiError(400, "HORARIO_INVALIDO", "El club atiende de 08:00 a 23:00")
    if (fecha_hora_fin - fecha_hora_inicio) not in DURACIONES_VALIDAS:
        raise ApiError(400, "DURACION_INVALIDA", "El intervalo debe durar una, dos o tres horas")

    ahora = datetime.now(GMT_MENOS_3).replace(tzinfo=None)
    if fecha_hora_inicio <= ahora:
        raise ApiError(400, "FECHA_NO_FUTURA", "El intervalo debe comenzar en un momento posterior al actual")

    if id_deporte is not None and (not isinstance(id_deporte, int) or isinstance(id_deporte, bool)):
        raise ApiError(400, "ID_DEPORTE_INVALIDO", "id_deporte debe ser un número entero")

    if techada is not None and not isinstance(techada, bool):
        raise ApiError(400, "TECHADA_INVALIDA", "techada debe ser true o false")

    canchas = canchas_repository.find_disponibles(fecha_hora_inicio, fecha_hora_fin, id_deporte, techada, limit, offset)
    total = canchas_repository.count_disponibles(fecha_hora_inicio, fecha_hora_fin, id_deporte, techada)
    return canchas, total