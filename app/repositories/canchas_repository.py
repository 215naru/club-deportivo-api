from app.db import get_db

def _fila_cancha(fila):
    if fila is None:
        return None
    fila["techada"] = bool(fila["techada"])
    fila["activa"] = bool(fila["activa"])
    return fila