@echo off
title Actualizador del Contador Global
cd /d "%~dp0"

echo ========================================================
echo        ACTUALIZADOR DEL CONTADOR GLOBAL
echo ========================================================
echo.
echo 1. Cerrando el programa si esta abierto...
taskkill /F /IM ContadorGlobal.exe >nul 2>nul
timeout /t 1 /nobreak >nul

echo 2. Descargando la ultima version desde la nube...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Yassir-bit/contador-api/main/ContadorGlobal.exe' -OutFile 'ContadorGlobal_nueva.exe'"

if exist ContadorGlobal_nueva.exe (
    move /y ContadorGlobal_nueva.exe ContadorGlobal.exe >nul
    echo.
    echo ========================================================
    echo  [OK] El programa se actualizo a la version mas reciente!
    echo ========================================================
    echo.
    echo Abriendo el programa actualizado...
    start "" ContadorGlobal.exe
) else (
    echo.
    echo [!] No se pudo descargar la actualizacion. Revisa tu conexion a internet.
    pause
)

exit
