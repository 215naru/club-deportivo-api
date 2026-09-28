import re
from app.repositories import socios_repository
from app.errors import ApiError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CAMPOS_SOCIO_CREATE = {"nombre", "email"}
CAMPOS_SOCIO_UPDATE = {"nombre", "email", "activo"}

def _validar_body_creacion(data):
    if not isinstance(data, dict):
        raise ApiError(400, "CUERPO_INVALIDO", "El cuerpo debe ser un objeto JSON")
    desconocidos = set(data.keys()) - CAMPOS_SOCIO_CREATE
    if desconocidos:
        raise ApiError(400, "CAMPO_DESCONOCIDO", "El cuerpo contiene campos desconocidos: " + ", ".join(sorted(desconocidos)))
    faltantes = CAMPOS_SOCIO_CREATE - set(data.keys())
    if faltantes:
        raise ApiError(400, "CAMPO_REQUERIDO", "Faltan campos obligatorios: " + ", ".join(sorted(faltantes)))

def _validar_body_actualizacion(data):
    if not isinstance(data, dict):
        raise ApiError(400, "CUERPO_INVALIDO", "El cuerpo debe ser un objeto JSON")
    if not data:
        raise ApiError(400, "CUERPO_VACIO", "El cuerpo no puede estar vacío")
    desconocidos = set(data.keys()) - CAMPOS_SOCIO_UPDATE
    if desconocidos:
        raise ApiError(400, "CAMPO_DESCONOCIDO", "El cuerpo contiene campos desconocidos: " + ", ".join(sorted(desconocidos)))

def listar_socios(limit, offset, nombre=None, activo=None):
    socios = socios_repository.find_all(limit, offset, nombre, activo)
    total = socios_repository.count(nombre, activo)
    return socios, total

def obtener_socio(id_socio):
    socio = socios_repository.find_by_id(id_socio)
    if socio is None:
        raise ApiError(404,"SOCIO_NO_ENCONTRADO","No existe un socio con ese id" )
    return socio

def crear_socio(data):
    _validar_body_creacion(data)
    nombre = data.get("nombre","").strip()
    email = data.get("email","").strip().lower()

    if not isinstance(data.get("nombre"), str):
        raise ApiError(400, "NOMBRE_INVALIDO", "El nombre debe ser texto")

    if not nombre:
        raise ApiError(400,"NOMBRE_INVALIDO","El nombre es obligatorio")

    if not EMAIL_PATTERN.match(email):
        raise ApiError(400,"EMAIL_INVALIDO","El email no tiene un formato valido")
    
    if socios_repository.find_by_email(email) is not None:
        raise ApiError(409,"EMAIL_DUPLICADO","Ya existe un socio con ese email")

    nuevo_id = socios_repository.insert(nombre, email)
    return socios_repository.find_by_id(nuevo_id)
    
def actualizar_socio(id_socio, data):
    socio = obtener_socio(id_socio)
    _validar_body_actualizacion(data)

    if not isinstance(data.get("nombre"), str):
        raise ApiError(400, "NOMBRE_INVALIDO", "nombre debe ser texto")
        
nombre = data.get("nombre", socio["nombre"]).strip()
    email = data.get("email", socio["email"]).strip().lower()
    activo = data.get("activo", socio["activo"])

    if not isinstance(activo, bool):
        raise ApiError(400, "ACTIVO_INVALIDO", "activo debe ser true o false")

    
    if not nombre:
        raise ApiError(400,"NOMBRE_INVALIDO","El nombre es obligatorio")

    if not EMAIL_PATTERN.match(email):
        raise ApiError(400,"EMAIL_INVALIDO","El email no tiene un formato válido")
    
    existente = socios_repository.find_by_email(email)

    if existente is not None and existente["id"] != id_socio:
        raise ApiError(409,"EMAIL_DUPLICADO","Ya existe un socio con ese email")

    socios_repository.update(id_socio, nombre, email, activo)
    return socios_repository.find_by_id(id_socio)