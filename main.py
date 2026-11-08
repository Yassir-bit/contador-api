"""
App ultra-simple: Un botón, un nombre, un contador.
Proyecto de aprendizaje para GitHub + Render + Supabase.
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor

# ── Configuración ──
DATABASE_URL = os.getenv("DATABASE_URL", "")

app = FastAPI(title="Contador de Clicks")


def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    """Crea la tabla si no existe al arrancar."""
    if not DATABASE_URL:
        print("⚠️  No hay DATABASE_URL configurada. La app arrancará sin base de datos.")
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
        print("✅ Tabla 'clicks' lista en Supabase.")
    except Exception as e:
        print(f"⚠️  Error conectando/creando tabla: {e}")


PAGE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contador de Clicks</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #121824;
            color: #f1f5f9;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 36px 32px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            text-align: center;
        }
        h1 { font-size: 22px; color: #38bdf8; margin-bottom: 6px; }
        .subtitle { font-size: 13px; color: #94a3b8; margin-bottom: 24px; }
        .counter-box {
            background: #0f172a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            border: 1px solid #1e293b;
        }
        .counter {
            font-size: 56px;
            font-weight: 800;
            color: #38bdf8;
            line-height: 1;
        }
        .counter-label { font-size: 14px; color: #cbd5e1; margin-top: 8px; }
        input[type="text"] {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid #475569;
            border-radius: 10px;
            background: #0f172a;
            color: #f8fafc;
            font-size: 15px;
            outline: none;
            margin-bottom: 14px;
            transition: border-color 0.2s;
        }
        input:focus { border-color: #38bdf8; }
        button {
            width: 100%;
            padding: 14px;
            background: #0284c7;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }
        button:hover { background: #0369a1; }
        button:active { transform: scale(0.98); }
        .msg {
            margin-top: 14px;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 13px;
            display: none;
        }
        .msg.ok { display: block; background: #064e3b; color: #6ee7b7; border: 1px solid #059669; }
        .msg.err { display: block; background: #7f1d1d; color: #fca5a5; border: 1px solid #b91c1c; }
        .history { margin-top: 24px; text-align: left; }
        .history h3 { font-size: 14px; color: #94a3b8; margin-bottom: 10px; }
        .history-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 14px;
            background: #0f172a;
            border-radius: 8px;
            margin-bottom: 6px;
            font-size: 13px;
            border: 1px solid #1e293b;
        }
        .history-item .num { color: #38bdf8; font-weight: 700; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🖱️ Contador de Clicks</h1>
        <p class="subtitle">Desplegado en Render + Supabase</p>

        <div class="counter-box">
            <div class="counter" id="counter">0</div>
            <p class="counter-label">Este botón se presionó <strong id="count-text">0</strong> veces</p>
        </div>

        <input type="text" id="nombre" placeholder="Escribe tu nombre..." maxlength="100">
        <button id="btn" onclick="hacerClick()">¡PRESIÓNAME!</button>

        <div class="msg" id="msg"></div>

        <div class="history" id="history-box" style="display:none">
            <h3>📋 Últimos registros:</h3>
            <div id="history-list"></div>
        </div>
    </div>

    <script>
        fetch('/api/estado')
            .then(r => r.json())
            .then(data => {
                document.getElementById('counter').textContent = data.total;
                document.getElementById('count-text').textContent = data.total;
                renderHistory(data.ultimos);
            })
            .catch(() => {});

        function hacerClick() {
            const nombre = document.getElementById('nombre').value.trim();
            const msg = document.getElementById('msg');

            if (!nombre) {
                msg.className = 'msg err';
                msg.textContent = 'Por favor escribe tu nombre primero.';
                return;
            }

            const btn = document.getElementById('btn');
            btn.disabled = true;
            btn.textContent = 'Registrando...';

            fetch('/api/click', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({nombre: nombre})
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('counter').textContent = data.total;
                document.getElementById('count-text').textContent = data.total;
                msg.className = 'msg ok';
                msg.textContent = '🎉 ' + nombre + ', tu click fue el #' + data.tu_numero;
                renderHistory(data.ultimos);
            })
            .catch(() => {
                msg.className = 'msg err';
                msg.textContent = 'Error al comunicar con el servidor.';
            })
            .finally(() => {
                btn.disabled = false;
                btn.textContent = '¡PRESIÓNAME!';
            });
        }

        document.getElementById('nombre').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') hacerClick();
        });

        function renderHistory(items) {
            if (!items || items.length === 0) return;
            document.getElementById('history-box').style.display = 'block';
            const list = document.getElementById('history-list');
            list.innerHTML = '';
            items.forEach(item => {
                list.innerHTML += '<div class="history-item"><span>' +
                    escapeHtml(item.nombre) + '</span><span class="num">#' +
                    item.numero_click + '</span></div>';
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE_HTML


@app.get("/api/estado")
def estado():
    if not DATABASE_URL:
        return {"total": 0, "ultimos": []}
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT COUNT(*) as total FROM clicks;")
        total = cur.fetchone()["total"]
        cur.execute("SELECT nombre, numero_click FROM clicks ORDER BY id DESC LIMIT 10;")
        ultimos = cur.fetchall()
        cur.close()
        conn.close()
        return {"total": total, "ultimos": ultimos}
    except Exception as e:
        return {"total": 0, "ultimos": [], "error": str(e)}


@app.post("/api/click")
def registrar_click(data: dict):
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return {"error": "Nombre requerido"}

    if not DATABASE_URL:
        return {"error": "Sin base de datos", "total": 0, "tu_numero": 0, "ultimos": []}

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

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

    cur.close()
    conn.close()
    return {"total": total, "tu_numero": siguiente, "ultimos": ultimos}


@app.get("/health")
def health():
    return {"status": "online", "app": "Contador de Clicks"}


@app.on_event("startup")
def startup():
    init_db()

