from app.db import get_db
from app.utils.datetime_utils import formatear_fecha_hora

def _fila_a_reserva(fila):
    if fila is None:
        return None
    fila["fecha_hora_inicio"] = formatear_fecha_hora(fila["fecha_hora_inicio"])
    fila["fecha_hora_fin"] = formatear_fecha_hora(fila["fecha_hora_fin"])
    return fila

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

def find_all(id_cancha, id_socio, estado, fecha_desde, fecha_hasta, limit, offset):
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
    return [_fila_a_reserva(fila) for fila in filas]

def count(id_cancha, id_socio, estado, fecha_desde, fecha_hasta):
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
    return _fila_a_reserva(fila)

def existe_solapamiento_cancha(id_cancha, inicio, fin):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id FROM reservas "
        "WHERE id_cancha = %s AND estado = 'confirmada' "
        "AND fecha_hora_inicio < %s AND fecha_hora_fin > %s "
        "LIMIT 1",
        (id_cancha, fin, inicio)
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila is not None

def existe_solapamiento_socio(id_socio, inicio, fin):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id FROM reservas "
        "WHERE id_socio = %s AND estado = 'confirmada' "
        "AND fecha_hora_inicio < %s AND fecha_hora_fin > %s "
        "LIMIT 1",
        (id_socio, fin, inicio)
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila is not None

def insert(id_socio, id_cancha, inicio, fin, precio_hora, precio_total):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total) "
        "VALUES (%s, %s, %s, %s, 'confirmada', %s, %s)",
        (id_socio, id_cancha, inicio, fin, precio_hora, precio_total)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id

def actualizar_estado(id_reserva, nuevo_estado):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE reservas SET estado = %s WHERE id = %s",
        (nuevo_estado, id_reserva)
    )
    db.commit()
    cursor.close()