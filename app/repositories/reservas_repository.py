from app.db import get_db

def _armar_filtros(id_cancha, id_socio, estado, fecha_desde, fecha_hasta):
    condiciones = []
    parametros = []

    if id_cancha is not None:
        condiciones.append("id_cancha = %s")
        parametros.append(id_cancha)
    if id_socio is not None:
        condiciones.append("id_socio = %s")
        parametros.append(id_socio)
    if estado is not None:
        condiciones.append("estado = %s")
        parametros.append(estado)
    if fecha_desde is not None:
        condiciones.append("DATE(fecha_hora_inicio) >= %s")
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        condiciones.append("DATE(fecha_hora_inicio) <= %s")
        parametros.append(fecha_hasta)

    if condiciones:
        return " WHERE " + " AND ".join(condiciones), parametros
    return "", parametros

def find_all(limit, offset, id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    where_sql, parametros = _armar_filtros(id_cancha, id_socio, estado, fecha_desde, fecha_hasta)
    sql = (
        "SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total "
        "FROM reservas" + where_sql + " ORDER BY id ASC LIMIT %s OFFSET %s"
    )
    cursor.execute(sql, parametros + [limit, offset])
    filas = cursor.fetchall()
    cursor.close()
    return filas

def count(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None):
    db = get_db()
    cursor = db.cursor()
    where_sql, parametros = _armar_filtros(id_cancha, id_socio, estado, fecha_desde, fecha_hasta)
    sql = "SELECT COUNT(*) FROM reservas" + where_sql
    cursor.execute(sql, parametros)
    total = cursor.fetchone()[0]
    cursor.close()
    return total

def find_by_id(id_reserva):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total "
        "FROM reservas WHERE id = %s",
        (id_reserva,)
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila

def find_conflict_cancha(id_cancha, fecha_hora_inicio, fecha_hora_fin):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM reservas "
        "WHERE id_cancha = %s AND estado = 'confirmada' "
        "AND fecha_hora_inicio < %s AND fecha_hora_fin > %s "
        "LIMIT 1",
        (id_cancha, fecha_hora_fin, fecha_hora_inicio)
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila

def find_conflict_socio(id_socio, fecha_hora_inicio, fecha_hora_fin):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM reservas "
        "WHERE id_socio = %s AND estado = 'confirmada' "
        "AND fecha_hora_inicio < %s AND fecha_hora_fin > %s "
        "LIMIT 1",
        (id_socio, fecha_hora_fin, fecha_hora_inicio)
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila

def insert(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id

def update_estado(id_reserva, nuevo_estado):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE reservas SET estado = %s WHERE id = %s",
        (nuevo_estado, id_reserva)
    )
    db.commit()
    cursor.close()
