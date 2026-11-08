@echo off
title Contador de Clicks
cd /d "%~dp0"
echo Abriendo servidor local en http://localhost:8000 ...
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause

