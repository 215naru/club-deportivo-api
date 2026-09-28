from app.db import get_db

def _fila_a_cancha(fila):
    if fila is None:
        return None
    fila["techada"] = bool(fila["techada"])
    fila["activa"] = bool(fila["activa"])
    return fila

def existe_deporte(id_deporte):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id FROM deportes WHERE id=%s",
        (id_deporte,)
    )
    fila = cursor.fetchone()
    cursor.close()
    return fila is not None

def count():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM canchas"
    )
    total = cursor.fetchone()[0]
    cursor.close()
    return total

def insert(nombre,id_deporte,precio_hora,techada,activa):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO canchas (nombre,id_deporte,precio_hora,techada,activa) VALUES (%s,%s,%s,%s,%s)",
        (nombre,id_deporte,precio_hora,techada,activa))
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id

def find_all(limit,offset):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id,nombre,id_deporte,precio_hora,techada,activa FROM canchas ORDER BY id ASC LIMIT %s OFFSET %s",
        (limit,offset))
    filas = cursor.fetchall()
    cursor.close()
    return [_fila_a_cancha(fila) for fila in filas]

def find_by_id(id_cancha):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id,nombre,id_deporte,precio_hora,techada,activa FROM canchas WHERE id=%s",
        (id_cancha,)
    )
    fila = cursor.fetchone()
    cursor.close()
    return _fila_a_cancha(fila)
    
def update(id_cancha,nombre,precio_hora,techada,activa):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE canchas SET nombre=%s, precio_hora=%s, techada=%s, activa=%s WHERE id=%s",
        (nombre, precio_hora, techada, activa, id_cancha)
    )
    db.commit()
    cursor.close()

def delete(id_cancha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM canchas WHERE id=%s",(id_cancha,))
    db.commit()
    cursor.close()

def _armar_filtros_disponibles(id_deporte, techada):
    condiciones = ["activa = TRUE"]
    parametros = []

    if id_deporte is not None:
        condiciones.append("id_deporte = %s")
        parametros.append(id_deporte)
    if techada is not None:
        condiciones.append("techada = %s")
        parametros.append(techada)

    return " AND ".join(condiciones), parametros

def find_disponibles(fecha_hora_inicio, fecha_hora_fin, id_deporte, techada, limit, offset):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    condiciones_sql, parametros = _armar_filtros_disponibles(id_deporte, techada)
    sql = (
        "SELECT id,nombre,id_deporte,precio_hora,techada,activa FROM canchas "
        "WHERE " + condiciones_sql + " AND id NOT IN ("
        "SELECT id_cancha FROM reservas WHERE estado = 'confirmada' "
        "AND fecha_hora_inicio < %s AND fecha_hora_fin > %s"
        ") ORDER BY id ASC LIMIT %s OFFSET %s"
    )
    cursor.execute(sql, parametros + [fecha_hora_fin, fecha_hora_inicio, limit, offset])
    filas = cursor.fetchall()
    cursor.close()
    return [_fila_a_cancha(fila) for fila in filas]

def count_disponibles(fecha_hora_inicio, fecha_hora_fin, id_deporte, techada):
    db = get_db()
    cursor = db.cursor()
    condiciones_sql, parametros = _armar_filtros_disponibles(id_deporte, techada)
    sql = (
        "SELECT COUNT(*) FROM canchas WHERE " + condiciones_sql + " AND id NOT IN ("
        "SELECT id_cancha FROM reservas WHERE estado = 'confirmada' "
        "AND fecha_hora_inicio < %s AND fecha_hora_fin > %s"
        ")"
    )
    cursor.execute(sql, parametros + [fecha_hora_fin, fecha_hora_inicio])
    total = cursor.fetchone()[0]
    cursor.close()
    return total