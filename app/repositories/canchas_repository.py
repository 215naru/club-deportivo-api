from app.db import get_db

def _fila_cancha(fila):
    if fila is None:
        return None
    fila["techada"] = bool(fila["techada"])
    fila["activa"] = bool(fila["activa"])
    return fila

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

def find_all():
    pass

def update():
    pass

def delete(id_cancha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM canchas WEHRE id=%s",(id_cancha))
    db.commit()
    cursor.close()