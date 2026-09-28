from app.db import get_db

def verificar_formato(fila):
    if fila is None:
        return None
    if fila.get("fecha"):
        fila["fecha"] = str(fila["fecha"])
    
    for hora in ["hora_inicio", "hora_fin"]:
        if fila.get(hora):
            valor = str(fila[hora])
            if len(valor) == 7:
                valor = "0" + valor
            fila[hora] = valor
    return fila
    
def insert(id_cancha, fecha, hora_inicio, hora_fin, motivo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO bloqueos (id_cancha, fecha, hora_inicio, hora_fin, motivo)"
        "VALUES (%s, %s, %s, %s, %s)",
        (id_cancha, fecha, hora_inicio, hora_fin, motivo)
    )
    db.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    return nuevo_id

def find_by_id(id_bloqueo):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, id_cancha, fecha, hora_inicio, hora_fin, motivo FROM bloqueos WHERE id = %s",
        (id_bloqueo,)
    )
    fila = cursor.fetchone()
    cursor.close()

    return verificar_formato(fila)
    
def delete(id_bloqueo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM bloqueos WHERE id = %s", (id_bloqueo,))
    db.commit()
    cursor.close()

def find_all(id_cancha=None, fecha=None, Limit=10, Offset=0):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, id_cancha, fecha, hora_inicio, hora_fin, motivo FROM bloqueos WHERE 1=1"
    params = []
    
    if id_cancha is not None:
        query += " AND id_cancha = %s"
        params.append(id_cancha)
    if fecha is not None:
        query += " AND fecha = %s"
        params.append(fecha)
        
    query += " ORDER BY id ASC LIMIT %s OFFSET %s"
    params.extend([Limit, Offset])
    
    cursor.execute(query, tuple(params))
    filas = cursor.fetchall()
    cursor.close()
    bloqueos_limpios = []
    for fila in filas:
        bloqueo_verificado = verificar_formato(fila)
        bloqueos_limpios.append(bloqueo_verificado)
    return bloqueos_limpios

def count(id_cancha=None, fecha=None):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM bloqueos WHERE 1=1"
    params = []
    
    if id_cancha is not None:
        query += " AND id_cancha = %s"
        params.append(id_cancha)
    if fecha is not None:
        query += " AND fecha = %s"
        params.append(fecha)
        
    cursor.execute(query, tuple(params))
    total = cursor.fetchone()[0]
    cursor.close()
    return total

def existe_superposicion_bloqueo(id_cancha, fecha, hora_inicio, hora_fin):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id FROM bloqueos
        WHERE id_cancha = %s 
          AND fecha = %s
          AND hora_inicio < %s 
          AND hora_fin > %s
        """,
        (id_cancha, fecha, hora_fin, hora_inicio))
        
    fila = cursor.fetchone()
    cursor.close()
    return fila is not None
    
