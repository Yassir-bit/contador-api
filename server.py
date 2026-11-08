"""
Servidor API en la nube (FastAPI) para Render.
Gestiona la base de datos PostgreSQL en Supabase.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "")

app = FastAPI(title="API Contador")


def get_db():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    return psycopg2.connect(DATABASE_URL)


def init_db():
    if not DATABASE_URL:
        print("⚠️ DATABASE_URL no configurada aún.")
        return
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                numero_click INT NOT NULL,
                fecha TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabla 'clicks' verificada en PostgreSQL.")
    except Exception as e:
        print(f"⚠️ Error conectando con BD: {e}")


class ClickRequest(BaseModel):
    nombre: str


@app.get("/health")
def health():
    return {"status": "online"}


@app.get("/api/version")
def version():
    return {
        "version": "1.1",
        "download_url": "https://raw.githubusercontent.com/Yassir-bit/contador-api/main/ContadorGlobal.exe"
    }


@app.get("/api/estado")
def obtener_estado():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT COUNT(*) as total FROM clicks;")
        total = cur.fetchone()["total"]
        cur.execute("SELECT nombre, numero_click FROM clicks ORDER BY id DESC LIMIT 10;")
        ultimos = cur.fetchall()
        return {"total": total, "ultimos": ultimos}
    finally:
        cur.close()
        conn.close()


@app.post("/api/click")
def registrar_click(req: ClickRequest):
    nombre = req.nombre.strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT COALESCE(MAX(numero_click), 0) + 1 AS siguiente FROM clicks;")
        siguiente = cur.fetchone()["siguiente"]

        cur.execute(
            "INSERT INTO clicks (nombre, numero_click) VALUES (%s, %s);",
            (nombre, siguiente)
        )
        conn.commit()

        cur.execute("SELECT COUNT(*) as total FROM clicks;")
        total = cur.fetchone()["total"]
        cur.execute("SELECT nombre, numero_click FROM clicks ORDER BY id DESC LIMIT 10;")
        ultimos = cur.fetchall()

        return {"total": total, "tu_numero": siguiente, "ultimos": ultimos}
    finally:
        cur.close()
        conn.close()


@app.on_event("startup")
def startup():
    init_db()

