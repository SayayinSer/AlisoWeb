@echo off
echo ==============================================
echo Empaquetando AlisoWeb para Produccion (cPanel)
echo ==============================================

set DEPLOY_DIR=dist_produccion
set BACKEND_DIR=%DEPLOY_DIR%\backend
set FRONTEND_DIR=%DEPLOY_DIR%\public_html

if exist %DEPLOY_DIR% rmdir /S /Q %DEPLOY_DIR%
mkdir %DEPLOY_DIR%
mkdir %BACKEND_DIR%
mkdir %FRONTEND_DIR%

echo [1/3] Copiando archivos del Frontend...
xcopy /E /I /Q css %FRONTEND_DIR%\css
xcopy /E /I /Q js %FRONTEND_DIR%\js
if exist assets xcopy /E /I /Q assets %FRONTEND_DIR%\assets > nul
if exist images xcopy /E /I /Q images %FRONTEND_DIR%\images > nul
copy index.html %FRONTEND_DIR%\ > nul
copy *.jpg %FRONTEND_DIR%\ > nul 2>&1
copy *.jpeg %FRONTEND_DIR%\ > nul 2>&1
copy *.png %FRONTEND_DIR%\ > nul 2>&1

echo [2/3] Copiando archivos del Backend...
xcopy /E /I /Q backend %BACKEND_DIR%
:: Eliminar archivos innecesarios de backend
if exist %BACKEND_DIR%\__pycache__ rmdir /S /Q %BACKEND_DIR%\__pycache__
if exist %BACKEND_DIR%\.pytest_cache rmdir /S /Q %BACKEND_DIR%\.pytest_cache

echo [3/3] Paquete listo.
echo ==============================================
echo Los archivos estan en la carpeta: %cd%\%DEPLOY_DIR%
echo Consulta el archivo instrucciones_cpanel.md para desplegar.
pause
