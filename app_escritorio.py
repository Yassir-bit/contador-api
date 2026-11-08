"""
Aplicación de Escritorio (Ventana pequeña en Tkinter).
Se conecta a la API en Render (o local) sin exponer credenciales de BD.
"""

import os
import sys
import json
import threading
import urllib.request
import urllib.error
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


def get_api_url():
    # 1. URL fija directa por defecto a Render
    default_url = "https://contador-api-egzb.onrender.com"

    # 2. Buscar servidor.txt al lado del .exe o del script
    candidates = [
        Path(sys.executable).resolve().parent / "servidor.txt",
        Path(__file__).resolve().parent / "servidor.txt",
        Path.cwd() / "servidor.txt"
    ]
    for p in candidates:
        if p.exists():
            try:
                line = p.read_text(encoding="utf-8").strip()
                if line and not line.startswith("#"):
                    return line.rstrip("/")
            except Exception:
                pass

    return os.getenv("API_URL", default_url).rstrip("/")


API_URL = get_api_url()


class ContadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contador")
        self.root.geometry("380x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#000000")

        self._build_ui()
        self.actualizar_estado()
        self._iniciar_auto_refresco()

    def _iniciar_auto_refresco(self):
        """Refresca automáticamente cada 3 segundos en segundo plano."""
        self.actualizar_estado()
        self.root.after(3000, self._iniciar_auto_refresco)

    def _build_ui(self):
        # Título
        lbl_titulo = tk.Label(
            self.root,
            text="🖱️ Contador Global",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#000000"
        )
        lbl_titulo.pack(pady=(16, 2))

        # Indicador de vivo / auto-refresco
        self.lbl_live = tk.Label(
            self.root,
            text="● Sincronizado en tiempo real (cada 3s)",
            font=("Segoe UI", 8),
            fg="#AAAAAA",
            bg="#000000"
        )
        self.lbl_live.pack(pady=(0, 10))

        # Cuadro del número de contador
        frame_counter = tk.Frame(self.root, bg="#111111", bd=1, relief=tk.SOLID, highlightbackground="#333333", highlightthickness=1)
        frame_counter.pack(padx=24, fill=tk.X, pady=(0, 16))

        self.lbl_count = tk.Label(
            frame_counter,
            text="0",
            font=("Segoe UI", 48, "bold"),
            fg="#FFFFFF",
            bg="#111111"
        )
        self.lbl_count.pack(pady=(12, 0))

        self.lbl_sub_count = tk.Label(
            frame_counter,
            text="clicks registrados en total",
            font=("Segoe UI", 9),
            fg="#888888",
            bg="#111111"
        )
        self.lbl_sub_count.pack(pady=(0, 12))

        # Input de Nombre
        frame_input = tk.Frame(self.root, bg="#000000")
        frame_input.pack(padx=24, fill=tk.X, pady=(0, 10))

        lbl_nombre = tk.Label(
            frame_input,
            text="Tu nombre:",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#000000"
        )
        lbl_nombre.pack(anchor="w", pady=(0, 4))

        self.ent_nombre = tk.Entry(
            frame_input,
            font=("Segoe UI", 11),
            bg="#111111",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor="#FFFFFF",
            highlightbackground="#444444"
        )
        self.ent_nombre.pack(fill=tk.X, ipady=6)
        self.ent_nombre.bind("<Return>", lambda e: self.enviar_click())

        # Botón principal
        self.btn_click = tk.Button(
            self.root,
            text="¡PRESIÓNAME!",
            font=("Segoe UI", 11, "bold"),
            fg="#000000",
            bg="#FFFFFF",
            activebackground="#CCCCCC",
            activeforeground="#000000",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.enviar_click
        )
        self.btn_click.pack(padx=24, fill=tk.X, ipady=8, pady=(0, 10))

        # Mensaje de estado
        self.lbl_msg = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#000000"
        )
        self.lbl_msg.pack(pady=(0, 8))

        # Lista de últimos
        lbl_hist = tk.Label(
            self.root,
            text="Últimas personas que presionaron:",
            font=("Segoe UI", 9, "bold"),
            fg="#888888",
            bg="#000000"
        )
        lbl_hist.pack(anchor="w", padx=26, pady=(0, 4))

        self.listbox = tk.Listbox(
            self.root,
            font=("Segoe UI", 9),
            bg="#111111",
            fg="#FFFFFF",
            selectbackground="#333333",
            selectforeground="#FFFFFF",
            relief=tk.FLAT,
            height=5,
            highlightthickness=1,
            highlightbackground="#333333"
        )
        self.listbox.pack(padx=24, fill=tk.BOTH, expand=True, pady=(0, 16))

    def actualizar_estado(self):
        def _fetch():
            try:
                req = urllib.request.Request(f"{API_URL}/api/estado")
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    self.root.after(0, lambda: self._render_estado(data))
            except Exception:
                self.root.after(0, lambda: self.lbl_msg.config(text="⚠️ Servidor iniciando... reintenta en breve", fg="#FBBF24"))

        threading.Thread(target=_fetch, daemon=True).start()

    def _render_estado(self, data):
        self.lbl_count.config(text=str(data.get("total", 0)))
        self.lbl_msg.config(text="")
        self.listbox.delete(0, tk.END)
        for item in data.get("ultimos", []):
            self.listbox.insert(tk.END, f" #{item['numero_click']} - {item['nombre']}")

    def enviar_click(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre:
            self.lbl_msg.config(text="Escribe tu nombre primero", fg="#F87171")
            self.ent_nombre.focus_set()
            return

        self.btn_click.config(state=tk.DISABLED, text="Enviando...")
        self.lbl_msg.config(text="Conectando con la nube...", fg="#38BDF8")

        def _enviar():
            try:
                payload = json.dumps({"nombre": nombre}).encode("utf-8")
                req = urllib.request.Request(
                    f"{API_URL}/api/click",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=35) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    self.root.after(0, lambda: self._on_click_success(data))
            except Exception:
                self.root.after(0, lambda: self.lbl_msg.config(text="Error al conectar con la API (reintentando)", fg="#F87171"))
            finally:
                self.root.after(0, lambda: self.btn_click.config(state=tk.NORMAL, text="¡PRESIÓNAME!"))

        threading.Thread(target=_enviar, daemon=True).start()

    def _on_click_success(self, data):
        self.lbl_count.config(text=str(data.get("total", 0)))
        self.lbl_msg.config(text=f"¡Registrado! Fuiste el #{data.get('tu_numero')}", fg="#4ADE80")
        self.ent_nombre.delete(0, tk.END)
        self.listbox.delete(0, tk.END)
        for item in data.get("ultimos", []):
            self.listbox.insert(tk.END, f" #{item['numero_click']} - {item['nombre']}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ContadorApp(root)
    root.mainloop()

