from app.repositories import canchas_repository
from app.errors import ApiError

def crear_cancha(data):
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

def listar_canchas(limit, offset):
    canchas = canchas_repository.find_all(limit, offset)
    total = canchas_repository.count()
    return canchas, total

def obtener_cancha(id_cancha):
    cancha = canchas_repository.find_by_id(id_cancha)
    if cancha is None:
        raise ApiError(404,"Cancha no encontrada")
    return cancha

def actualizar_cancha(id_cancha, data):
    cancha = obtener_cancha(id_cancha)

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
    canchas_repository.delete(id_cancha)