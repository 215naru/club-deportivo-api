from app.db import get_db

def find_all():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC")
    filas = cursor.fetchall()
    cursor.close()
    return filas
