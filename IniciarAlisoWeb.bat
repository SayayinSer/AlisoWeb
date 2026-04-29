@echo off
title AlisoWeb - Lanzador de Entorno
color 0A

echo ==================================================
echo        INICIANDO ENTORNO ALISO WEB (LAMP DEV)
echo ==================================================
echo.

:: 1. Iniciar el Backend (FastAPI + MySQL) en una nueva ventana
echo Iniciando Servidor Backend (API)...
start "AlisoWeb Backend (API)" /D "%~dp0backend" cmd /k "python -m uvicorn main:app --port 8001 --reload"

:: 2. Iniciar el Frontend (Static) en una nueva ventana
echo Iniciando Servidor Frontend (HTML/CSS/JS)...
start "AlisoWeb Frontend" /D "%~dp0" cmd /k "python -m http.server 8000"

:: 3. Esperar un par de segundos para asegurar que los servidores levantaron
timeout /t 3 > nul

:: 4. Abrir los enlaces principales en el navegador predeterminado
echo Abriendo sitio web en el navegador...
start http://localhost:8000
start http://localhost:8001/admin

echo.
echo ==================================================
echo TODO LISTO. LOS SERVIDORES ESTAN CORRIENDO.
echo ==================================================
echo - Sitio Web (Frontend): http://localhost:8000
echo - API Backend:          http://localhost:8001
echo - Panel de Admin:       http://localhost:8001/admin
echo.
echo Para apagar los servidores, cierra las ventanas CMD adicionales 
echo que se abrieron (llamadas "AlisoWeb Backend" y "AlisoWeb Frontend").
echo.
pause
