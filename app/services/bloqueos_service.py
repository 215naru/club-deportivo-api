from datetime import datetime, date
from app.repositories import bloqueos_repository, canchas_repository
from app.errors import ApiError

def crear_bloqueo(data):
    id_cancha = data.get("id_cancha")
    fecha_str = data.get("fecha")
    hora_inicio = data.get("hora_inicio")
    hora_fin = data.get("hora_fin")
    motivo = data.get("motivo", "").strip()

    if not id_cancha or not fecha_str or not hora_inicio or not hora_fin or not motivo:
        raise ApiError(400, "DATOS_INVALIDOS", "Todos los campos son obligatorios")

    cancha = canchas_repository.find_by_id(id_cancha)
    if cancha is None:
        raise ApiError(404, "CANCHA_NO_ENCONTRADA", "No existe una cancha con ese id")

    if not hora_inicio.endswith(":00:00") or not hora_fin.endswith(":00:00"):
        raise ApiError(400, "HORARIO_INVALIDO", "Las horas deben ser en punto (ej: 08:00:00)")

    if hora_inicio < "08:00:00" or hora_fin > "23:00:00" or hora_inicio >= hora_fin:
        raise ApiError(400, "HORARIO_INVALIDO", "El horario debe ser entre las 08:00:00 y las 23:00:00")

    fecha_bloqueo = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    if fecha_bloqueo < date.today():
        raise ApiError(400, "FECHA_INVALIDA", "No se pueden crear bloqueos en el pasado")

    if bloqueos_repository.existe_superposicion_bloqueo(id_cancha, fecha_str, hora_inicio, hora_fin):
        raise ApiError(409, "SUPERPOSICION", "Ya existe un bloqueo en ese horario para esta cancha")

    nuevo_id = bloqueos_repository.insert(id_cancha, fecha_str, hora_inicio, hora_fin, motivo)

    return bloqueos_repository.find_by_id(nuevo_id)

def listar_bloqueos(limit, offset, id_cancha=None, fecha=None):
    
    bloqueos = bloqueos_repository.find_all(id_cancha=id_cancha, fecha=fecha, Limit=limit, Offset=offset)
    total = bloqueos_repository.count(id_cancha=id_cancha, fecha=fecha)

    return bloqueos, total

def eliminar_bloqueo(id_bloqueo):
    bloqueo = bloqueos_repository.find_by_id(id_bloqueo)

    if bloqueo is None:
        raise ApiError(404, "BLOQUEO_NO_ENCONTRADO", "No existe un bloqueo con ese id")
    bloqueos_repository.delete(id_bloqueo)
