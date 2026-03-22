import sqlite3

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    telefono TEXT,
    estado TEXT,
    ciudad TEXT,
    ultimo_mensaje TEXT
)
""")
conn.commit()


def guardar_lead(telefono, estado, ciudad="", mensaje=""):
    cursor.execute("""
    INSERT OR REPLACE INTO leads (telefono, estado, ciudad, ultimo_mensaje)
    VALUES (?, ?, ?, ?)
    """, (telefono, estado, ciudad, mensaje))
    conn.commit()


def obtener_estado(telefono):
    cursor.execute("SELECT estado FROM leads WHERE telefono=?", (telefono,))
    result = cursor.fetchone()
    return result[0] if result else "inicio"