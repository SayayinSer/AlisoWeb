@echo off
title AlisoWeb - Backup y Sincronizacion GitHub
color 0B

echo ==================================================
echo   CREANDO BACKUP LOCAL Y SINCRONIZANDO CON GITHUB
echo ==================================================
echo.

:: 1. Crear Backup Local (.zip)
set BACKUP_NAME=AlisoWeb_Backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.zip
echo [1/3] Creando copia de seguridad local: %BACKUP_NAME%
:: Usando PowerShell para comprimir todos los archivos y carpetas, excluyendo archivos pesados e innecesarios
powershell -Command "Get-ChildItem -Exclude '.git', 'dist_produccion', '__pycache__', '*.zip' | Compress-Archive -DestinationPath '%BACKUP_NAME%' -Force"
echo Backup local creado exitosamente.
echo.

:: 2. Sincronizar con GitHub
echo [2/3] Agregando cambios a Git...
git add .

echo [3/3] Subiendo cambios a GitHub...
git commit -m "Actualizacion: Integracion cPanel, Base de Datos MySQL y Entorno Admin (Automated Backup)"
git push origin main

echo.
echo ==================================================
echo   PROCESO COMPLETADO EXITOSAMENTE
echo ==================================================
echo El backup fue guardado como: %BACKUP_NAME%
echo Todos los cambios estan en GitHub.
pause
