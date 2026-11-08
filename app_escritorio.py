"""
Aplicación de Escritorio (Ventana pequeña en Tkinter).
Se conecta a la API en Render (o local) sin exponer credenciales de BD.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


def get_api_url():
    # 1. Archivo servidor.txt al lado del script o ejecutable
    txt_path = Path(__file__).resolve().parent / "servidor.txt"
    if txt_path.exists():
        try:
            line = txt_path.read_text(encoding="utf-8").strip()
            if line and not line.startswith("#"):
                return line.rstrip("/")
        except Exception:
            pass
    # 2. Variable de entorno
    return os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


API_URL = get_api_url()


class ContadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contador")
        self.root.geometry("380x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#1E293B")

        self._build_ui()
        self.actualizar_estado()

    def _build_ui(self):
        # Título
        lbl_titulo = tk.Label(
            self.root,
            text="🖱️ Contador Global",
            font=("Segoe UI", 16, "bold"),
            fg="#38BDF8",
            bg="#1E293B"
        )
        lbl_titulo.pack(pady=(20, 2))

        lbl_sub = tk.Label(
            self.root,
            text="Presiona el botón para registrar tu turno",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#1E293B"
        )
        lbl_sub.pack(pady=(0, 16))

        # Cuadro del número de contador
        frame_counter = tk.Frame(self.root, bg="#0F172A", bd=1, relief=tk.SOLID)
        frame_counter.pack(padx=24, fill=tk.X, pady=(0, 16))

        self.lbl_count = tk.Label(
            frame_counter,
            text="0",
            font=("Segoe UI", 48, "bold"),
            fg="#38BDF8",
            bg="#0F172A"
        )
        self.lbl_count.pack(pady=(12, 0))

        self.lbl_sub_count = tk.Label(
            frame_counter,
            text="clicks registrados en total",
            font=("Segoe UI", 9),
            fg="#CBD5E1",
            bg="#0F172A"
        )
        self.lbl_sub_count.pack(pady=(0, 12))

        # Input de Nombre
        frame_input = tk.Frame(self.root, bg="#1E293B")
        frame_input.pack(padx=24, fill=tk.X, pady=(0, 10))

        lbl_nombre = tk.Label(
            frame_input,
            text="Tu nombre:",
            font=("Segoe UI", 9, "bold"),
            fg="#F1F5F9",
            bg="#1E293B"
        )
        lbl_nombre.pack(anchor="w", pady=(0, 4))

        self.ent_nombre = tk.Entry(
            frame_input,
            font=("Segoe UI", 11),
            bg="#0F172A",
            fg="#FFFFFF",
            insertbackground="#38BDF8",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor="#38BDF8",
            highlightbackground="#475569"
        )
        self.ent_nombre.pack(fill=tk.X, ipady=6)
        self.ent_nombre.bind("<Return>", lambda e: self.enviar_click())

        # Botón principal
        self.btn_click = tk.Button(
            self.root,
            text="¡PRESIÓNAME!",
            font=("Segoe UI", 11, "bold"),
            fg="#FFFFFF",
            bg="#0284C7",
            activebackground="#0369A1",
            activeforeground="#FFFFFF",
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
            fg="#4ADE80",
            bg="#1E293B"
        )
        self.lbl_msg.pack(pady=(0, 8))

        # Lista de últimos
        lbl_hist = tk.Label(
            self.root,
            text="Últimas personas que presionaron:",
            font=("Segoe UI", 9, "bold"),
            fg="#94A3B8",
            bg="#1E293B"
        )
        lbl_hist.pack(anchor="w", padx=26, pady=(0, 4))

        self.listbox = tk.Listbox(
            self.root,
            font=("Segoe UI", 9),
            bg="#0F172A",
            fg="#E2E8F0",
            selectbackground="#0284C7",
            relief=tk.FLAT,
            height=5,
            highlightthickness=1,
            highlightbackground="#334155"
        )
        self.listbox.pack(padx=24, fill=tk.BOTH, expand=True, pady=(0, 16))

    def actualizar_estado(self):
        try:
            req = urllib.request.Request(f"{API_URL}/api/estado")
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                self.lbl_count.config(text=str(data.get("total", 0)))
                self.listbox.delete(0, tk.END)
                for item in data.get("ultimos", []):
                    self.listbox.insert(tk.END, f" #{item['numero_click']} - {item['nombre']}")
        except Exception:
            self.lbl_msg.config(text="⚠️ Servidor desconectado", fg="#F87171")

    def enviar_click(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre:
            self.lbl_msg.config(text="Escribe tu nombre primero", fg="#F87171")
            self.ent_nombre.focus_set()
            return

        self.btn_click.config(state=tk.DISABLED, text="Enviando...")
        self.root.update_idletasks()

        try:
            payload = json.dumps({"nombre": nombre}).encode("utf-8")
            req = urllib.request.Request(
                f"{API_URL}/api/click",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))
                self.lbl_count.config(text=str(data.get("total", 0)))
                self.lbl_msg.config(text=f"¡Registrado! Fuiste el #{data.get('tu_numero')}", fg="#4ADE80")
                self.ent_nombre.delete(0, tk.END)
                
                self.listbox.delete(0, tk.END)
                for item in data.get("ultimos", []):
                    self.listbox.insert(tk.END, f" #{item['numero_click']} - {item['nombre']}")
        except Exception as e:
            self.lbl_msg.config(text="Error al conectar con la API", fg="#F87171")
        finally:
            self.btn_click.config(state=tk.NORMAL, text="¡PRESIÓNAME!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ContadorApp(root)
    root.mainloop()
