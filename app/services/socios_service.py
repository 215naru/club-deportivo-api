import re
from app.repositories import socios_repository
from app.errors import ApiError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def listar_socios(limit, offset):
    socios = socios_repository.find_all(limit, offset)
    total = socios_repository.count()
    return socios, total

def obtener_socio(id_socio):
    socio = socios_repository.find_by_id(id_socio)
    if socio is None:
        raise ApiError(404,"SOCIO_NO_ENCONTRADO","No existe un socio con ese id" )
    return socio

def crear_socio(data):
    nombre = data.get("nombre","").strip()
    email = data.get("email","").strip().lower()

    if not nombre:
        raise ApiError(400,"NOMBRE_INVALIDO","El nombre es obligatorio")

    if not EMAIL_PATTERN.match(email):
        raise ApiError(400,"EMAIL_INVALIDO","El email no tiene un formato valido")
    
    if socios_repository.find_by_email(email) is not None:
        raise ApiError(409,"EMAIL_DUPLICADO","Ya existe un socio con ese email")

    nuevo_id = socios_repository.insert(nombre, email)
    return nuevo_id
    
def actualizar_socio(id_socio, data):
    socio = obtener_socio(id_socio)
    nombre = data.get("nombre", socio["nombre"]).strip()
    email = data.get("email", socio["email"]).strip().lower()
    activo = data.get("activo", socio["activo"])

    if not nombre:
        raise ApiError(400,"NOMBRE_INVALIDO","El nombre es obligatorio")

    if not EMAIL_PATTERN.match(email):
        raise ApiError(400,"EMAIL_INVALIDO","El email no tiene un formato válido")
    
    existente = socios_repository.find_by_email(email)

    if existente is not None and existente["id"] != id_socio:
        raise ApiError(409,"EMAIL_DUPLICADO","Ya existe un socio con ese email")

    socios_repository.update(id_socio, nombre, email, activo)
    return socios_repository.find_by_id(id_socio)