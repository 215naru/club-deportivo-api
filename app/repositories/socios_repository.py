from app.db import get_db
def _fila_a_socio(fila):
    if fila is None:
        return None
    fila["activo"] = bool(fila["activo"])
    return fila

def _armar_filtros(nombre, activo):
    condiciones = []
    parametros = []

    if nombre is not None:
        condiciones.append("LOWER(nombre) LIKE %s")
        parametros.append(f"%{nombre.lower()}%")
    if activo is not None:
        condiciones.append("activo = %s")
        parametros.append(activo)

    if condiciones:
        return " WHERE " + " AND ".join(condiciones), parametros
    return "", parametros

def find_all(limit, offset, nombre=None, activo=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    where_sql, parametros = _armar_filtros(nombre, activo)
    sql = (
        "SELECT id,nombre,email,activo FROM socios" + where_sql
        + " ORDER BY id ASC LIMIT %s OFFSET %s"
    )
    cursor.execute(sql, parametros + [limit, offset])
    filas = cursor.fetchall()
    cursor.close()
    return [_fila_a_socio(fila) for fila in filas]

def count(nombre=None, activo=None):
    db = get_db()
    cursor = db.cursor()
    where_sql, parametros = _armar_filtros(nombre, activo)
    cursor.execute("SELECT COUNT(*) FROM socios" + where_sql, parametros)
    total = cursor.fetchone()[0]
    cursor.close()
    return total

def find_by_id(id_socio):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, email, activo FROM socios WHERE id = %s",
        (id_socio,),
    )
    socio = cursor.fetchone()
    cursor.close()
    return _fila_a_socio(socio)

def find_by_email(email):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, email, activo FROM socios WHERE email = %s",
        (email,),
    )
    fila = cursor.fetchone()
    cursor.close()
    return _fila_a_socio(fila)

def insert(nombre, email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, TRUE)",
        (nombre, email),
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id

def update(id_socio, nombre, email, activo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE socios SET nombre = %s, email = %s, activo = %s WHERE id= %s",
        (nombre, email, activo, id_socio))
    db.commit()
    cursor.close()