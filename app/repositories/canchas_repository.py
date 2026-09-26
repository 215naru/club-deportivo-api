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
        (id_deporte)
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
        "SELECT id,nombre,id_deporte,precio_hora,techada,activa FROM canchas WHERE id=%s",(id_cancha)
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
    cursor.execute("DELETE FROM canchas WEHRE id=%s",(id_cancha))
    db.commit()
    cursor.close()