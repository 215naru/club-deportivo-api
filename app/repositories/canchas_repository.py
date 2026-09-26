from app.db import get_db

def _fila_cancha(fila):
    if fila is None:
        return None
    fila["techada"] = bool(fila["techada"])
    fila["activa"] = bool(fila["activa"])
    return fila

def insert():
    pass

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