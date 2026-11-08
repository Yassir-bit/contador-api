# 🖱️ Contador Global Multi-PC (Intento 2)

Aplicación ligera de escritorio con sincronización en tiempo real a través de una API en la nube y base de datos centralizada PostgreSQL.

---

## 📌 ¿Qué hace este proyecto?
Permite que múltiples usuarios desde diferentes computadoras hagan clic en un botón común, registrando cada pulsación en una base de datos en la nube y mostrando en tiempo real:
* Contador total acumulado.
* Ranking de usuarios con más clics.
* Historial de los últimos registros.

---

## 🏗️ Arquitectura
* **Cliente de Escritorio:** Python (Tkinter) compilado en ejecutable portable (`ContadorGlobal.exe`). No expone credenciales directas a la base de datos.
* **Backend API:** FastAPI (`server.py`) desplegado en **Render**.
* **Base de Datos:** PostgreSQL en la nube (**Supabase**), tabla `clicks`.

---

## 📁 Archivos Principales
| Archivo | Descripción |
|---|---|
| `app_escritorio.py` | Código fuente de la interfaz gráfica de usuario (Tkinter). |
| `server.py` | API REST con endpoints (`/click`, `/total`, `/historial`, `/ranking`). |
| `servidor.txt` | Contiene la URL pública del backend en Render. |
| `ContadorGlobal.exe` | Ejecutable listo para usar sin necesidad de instalar Python. |
| `ABRIR_APP.bat` | Acceso rápido para lanzar la aplicación de escritorio. |
| `ACTUALIZAR_APP.bat` | Script para recompilar el ejecutable y generar el `.zip` distribuible. |
| `INICIAR_LOCAL.bat` | Inicia el servidor FastAPI localmente para pruebas. |

---

## 🚀 Uso Rápido
1. **Ejecutar la aplicación:**  
   Doble clic en `ContadorGlobal.exe` o ejecuta `ABRIR_APP.bat`.
2. **Ingresar un nombre:**  
   Escribe tu nombre o alias y pulsa el botón **¡CLICK!**.
3. **Distribuir a otras PC:**  
   Comparte el archivo `Contador_Para_Otras_PC.zip` con cualquier usuario de Windows.

