<#
.SYNOPSIS
    Script de empaquetado profesional para produccion (cPanel / Servidores Estandar).
#>
$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   EMPAQUETANDO ALISO WEB PARA PRODUCCION (cPanel / Apache) " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$baseDir = "D:\aaProyectos\Entorno03\AlisoWeb"
$deployDir = Join-Path $baseDir "dist_produccion"
$frontendDir = Join-Path $deployDir "public_html"
$backendDir = Join-Path $deployDir "backend"

if (Test-Path $deployDir) {
    Write-Host "Limpiando directorio previo dist_produccion..." -ForegroundColor Yellow
    Remove-Item $deployDir -Recurse -Force
}

New-Item -ItemType Directory -Path $frontendDir -Force | Out-Null
New-Item -ItemType Directory -Path $backendDir -Force | Out-Null

Write-Host "`n[1/4] Copiando y optimizando Frontend (public_html)..." -ForegroundColor Yellow
# Copiar css, js, assets
robocopy (Join-Path $baseDir "css") (Join-Path $frontendDir "css") /E /NFL /NDL /NJH /NJS /R:0 /W:0 | Out-Null
robocopy (Join-Path $baseDir "js") (Join-Path $frontendDir "js") /E /NFL /NDL /NJH /NJS /R:0 /W:0 | Out-Null
if (Test-Path (Join-Path $baseDir "assets")) {
    robocopy (Join-Path $baseDir "assets") (Join-Path $frontendDir "assets") /E /NFL /NDL /NJH /NJS /R:0 /W:0 | Out-Null
}

# Copiar index.html y logos
Copy-Item (Join-Path $baseDir "index.html") $frontendDir -Force
Get-ChildItem $baseDir -Filter "*.jpeg" | Copy-Item -Destination $frontendDir -Force
Get-ChildItem $baseDir -Filter "*.jpg" | Copy-Item -Destination $frontendDir -Force
Get-ChildItem $baseDir -Filter "*.png" | Copy-Item -Destination $frontendDir -Force

# Generar .htaccess optimizado para public_html
$htaccessLines = @(
    "# ==============================================================================",
    "# .htaccess para Frontend de Aliso Web Solution",
    "# ==============================================================================",
    "<IfModule mod_rewrite.c>",
    "    RewriteEngine On",
    "    RewriteBase /",
    "    # Forzar HTTPS",
    "    RewriteCond %{HTTPS} off",
    "    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]",
    "</IfModule>",
    "",
    "# Compresion Gzip / Brotli",
    "<IfModule mod_deflate.c>",
    "    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json",
    "</IfModule>",
    "",
    "# Cache headers para estaticos",
    "<IfModule mod_expires.c>",
    "    ExpiresActive On",
    "    ExpiresByType image/jpg `"access plus 1 year`"",
    "    ExpiresByType image/jpeg `"access plus 1 year`"",
    "    ExpiresByType image/gif `"access plus 1 year`"",
    "    ExpiresByType image/png `"access plus 1 year`"",
    "    ExpiresByType text/css `"access plus 1 month`"",
    "    ExpiresByType application/javascript `"access plus 1 month`"",
    "</IfModule>"
)
$htaccessLines | Set-Content -Path (Join-Path $frontendDir ".htaccess") -Encoding UTF8
Write-Host "  [OK] Frontend empaquetado con .htaccess optimizado." -ForegroundColor Green

Write-Host "`n[2/4] Copiando Backend Python para Passenger WSGI..." -ForegroundColor Yellow
$srcBackend = Join-Path $baseDir "backend"
robocopy $srcBackend $backendDir /E /XD "__pycache__" ".pytest_cache" "uploads" /XF "*.pyc" "test.db" /NFL /NDL /NJH /NJS /R:0 /W:0 | Out-Null

# Crear carpeta uploads limpia
New-Item -ItemType Directory -Path (Join-Path $backendDir "uploads") -Force | Out-Null

# Generar .env.production.example
$envProdLines = @(
    "# Configuracion de Produccion para cPanel / Servidor Estandar",
    "DATABASE_URL=`"mysql+pymysql://usuario_cpanel:contraseña_segura@localhost/nombre_basededatos`"",
    "DEBUG=False",
    "APP_NAME=`"Aliso Web Solution API`"",
    "API_PORT=8001",
    "CORS_ORIGINS=`"https://aliso.com.ar,https://www.aliso.com.ar`""
)
$envProdLines | Set-Content -Path (Join-Path $backendDir ".env.production.example") -Encoding UTF8
Write-Host "  [OK] Backend empaquetado con .env.production.example y passenger_wsgi.py." -ForegroundColor Green

Write-Host "`n[3/4] Generando Guia de Despliegue en Produccion..." -ForegroundColor Yellow
$deployGuideLines = @(
    '# Guía Rápida de Despliegue en cPanel / Servidor Estándar',
    '',
    '## 1. Frontend (public_html)',
    '- Subir el contenido de la carpeta `public_html/` a la raíz web de tu dominio en cPanel (`/public_html/` o directorio raíz asignado).',
    '',
    '## 2. Backend (alisoweb_backend)',
    '- Subir el contenido de `backend/` a una carpeta privada en el servidor, por ejemplo `/home/usuario/alisoweb_backend/`.',
    '- En cPanel, ingresar a **Setup Python App**:',
    '  - **Python Version**: 3.10, 3.11 o superior.',
    '  - **Application Root**: `alisoweb_backend`',
    '  - **Application URL**: `/api` (o subdominio `api.aliso.com.ar`).',
    '  - **Application Startup File**: `passenger_wsgi.py`',
    '  - **Application Entry Point**: `application`',
    '- Instalar dependencias mediante `pip install -r requirements.txt`.',
    '- Configurar el archivo `.env` renombrando `.env.production.example` con tus credenciales de MySQL.',
    '',
    '## 3. Base de Datos',
    '- Crear la base de datos MySQL en cPanel y otorgar todos los privilegios al usuario creado.',
    '- Al iniciar la aplicación, las tablas se verificarán y crearán automáticamente.'
)
$deployGuideLines | Set-Content -Path (Join-Path $deployDir "INSTRUCCIONES_DESPLIEGUE.md") -Encoding UTF8
Write-Host "  [OK] Guia de despliegue generada." -ForegroundColor Green

Write-Host "`n[4/4] Comprimiendo paquete final ZIP para subida directa..." -ForegroundColor Yellow
$zipFileName = "AlisoWeb_Produccion_$timestamp.zip"
$zipFilePath = Join-Path $deployDir $zipFileName
# Comprimir solo los directorios public_html, backend y la guia
Compress-Archive -Path (Join-Path $frontendDir "*"), (Join-Path $backendDir "*"), (Join-Path $deployDir "INSTRUCCIONES_DESPLIEGUE.md") -DestinationPath $zipFilePath -CompressionLevel Optimal -Force
Write-Host "  [OK] Archivo ZIP creado: $zipFilePath" -ForegroundColor Green

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "   ¡EMPAQUETADO PARA PRODUCCION COMPLETADO CON EXITO!       " -ForegroundColor Green
Write-Host "   Carpeta: $deployDir                                      " -ForegroundColor Yellow
Write-Host "   Archivo: $zipFileName                                    " -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
