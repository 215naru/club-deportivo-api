from app.db import get_db

def _fila_a_reserva(fila):
    if fila is None:
        return None
    return fila

def find_by_id(id_reserva):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT id,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total FROM reservas WHERE id = %s""",
        (id_reserva,))
    fila = cursor.fetchone()
    cursor.close()
    return _fila_a_reserva(fila)

def find_conflict_cancha(id_cancha,fecha_hora_inicio,fecha_hora_fin):
    """
    Busca una reserva CONFIRMADA que se superponga
    con el intervalo solicitado para una cancha.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT id,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total FROM reservas WHERE id_cancha = %s AND estado = 'confirmada' AND fecha_hora_inicio < %s AND fecha_hora_fin > %s LIMIT 1""",
        (id_cancha,fecha_hora_fin,fecha_hora_inicio))
    fila = cursor.fetchone()
    cursor.close()
    return _fila_a_reserva(fila)

def find_conflict_socio(id_socio,fecha_hora_inicio,fecha_hora_fin):
    """
    Busca una reserva CONFIRMADA que se superponga
    con el intervalo solicitado para un socio.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT id,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total FROM reservas WHERE id_socio = %s AND estado = 'confirmada' AND fecha_hora_inicio < %s AND fecha_hora_fin > %s LIMIT 1""",
        (id_socio,fecha_hora_fin,fecha_hora_inicio))
    fila = cursor.fetchone()
    cursor.close()
    return _fila_a_reserva(fila)

def insert(id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO reservas (id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total))
    db.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    return nuevo_id

def update_estado(id_reserva, estado):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """UPDATE reservas SET estado = %s WHERE id = %s""",
        (estado,id_reserva))
    db.commit()
    cursor.close()

def find_all(limit,offset,id_cancha=None,id_socio=None,estado=None,fecha_desde=None,fecha_hasta=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """SELECT id,id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total FROM reservas WHERE 1 = 1"""
    parametros = []
    if id_cancha is not None:
        query += " AND id_cancha = %s"
        parametros.append(id_cancha)
    if id_socio is not None:
        query += " AND id_socio = %s"
        parametros.append(id_socio)
    if estado is not None:
        query += " AND estado = %s"
        parametros.append(estado)
    if fecha_desde is not None:
        query += " AND DATE(fecha_hora_inicio) >= %s"
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        query += " AND DATE(fecha_hora_inicio) <= %s"
        parametros.append(fecha_hasta)
    query += """ ORDER BY id ASC LIMIT %s OFFSET %s"""
    parametros.extend([limit,offset])
    cursor.execute(query,tuple(parametros))
    filas = cursor.fetchall()
    cursor.close()
    return [_fila_a_reserva(fila)for fila in filas]

def count(id_cancha=None,id_socio=None,estado=None,fecha_desde=None,fecha_hasta=None):
    db = get_db()
    cursor = db.cursor()
    query = """SELECT COUNT(*) FROM reservas WHERE 1 = 1"""
    parametros = []
    if id_cancha is not None:
        query += " AND id_cancha = %s"
        parametros.append(id_cancha)
    if id_socio is not None:
        query += " AND id_socio = %s"
        parametros.append(id_socio)
    if estado is not None:
        query += " AND estado = %s"
        parametros.append(estado)
    if fecha_desde is not None:
        query += " AND DATE(fecha_hora_inicio) >= %s"
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        query += " AND DATE(fecha_hora_inicio) <= %s"
        parametros.append(fecha_hasta)
    cursor.execute(query,tuple(parametros))
    total = cursor.fetchone()[0]
    cursor.close()
    return total
