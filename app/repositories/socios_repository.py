from app.db import get_db

def find_all(limit, offset):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id,nomnbre,email,activo FROM socios ORDER BY id ASC LIMIT %s OFFSET %s",
        (limit, offset),
    )
    socios = cursor.fetchall()
    cursor.close()
    return socios

def count():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM socios")
    total = cursor.fetchone()[0]
    cursor.close
    return total

def find_by_id(id_socio):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, email, activo FROM socios WHERE id = %s",
        (id_socio,),
    )
    socio = cursor.fetchone()
    cursor.close()
    return socio

def find_by_email(email):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, email, activo FROM socios WHERE email = %s",
        (email,),
    )
    socio = cursor.fetchone()
    cursor.close()
    return socio

def insert(nombre, email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, TRUE)",
        (nombre, email),
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id

def update(id, nombre, email, activo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE socios SET nombre = %s, email = %s, activo = %s WHERE id= %s",
        (nombre, email, activo))
    db.commit()
    cursor.close()