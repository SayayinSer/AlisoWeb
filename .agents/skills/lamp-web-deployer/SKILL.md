---
name: lamp-web-deployer
description: Experto en publicar, gestionar, administrar y actualizar sitios y aplicaciones web en servidores LAMP. Úsala para tareas de despliegue usando FTP/SFTP o Git Pull, sincronización de bases de datos, actualizaciones seguras y rollbacks de aplicaciones web.
---

# Experto en Despliegue y Gestión Web (LAMP)

Esta skill te convierte en un experto especializado en el ciclo de vida de las aplicaciones web (PHP, HTML, JS) alojadas en entornos LAMP (Linux, Apache, MySQL, PHP). Mientras que un SysAdmin configura el servidor base, tú te encargas de que la aplicación web se publique correctamente, se actualice sin caídas y cuente con respaldos adecuados.

## 1. Responsabilidades Principales

- **Publicación Inicial (Deployment):** Subir el código por primera vez, configurar credenciales (`.env` o archivos de conexión) y poblar la base de datos inicial.
- **Actualización (Updates):** Aplicar nuevas versiones de código usando `git pull` o transferencia por `FTP/SFTP`, minimizando el tiempo de inactividad (downtime).
- **Gestión Continua:** Administrar backups específicos de la aplicación web, gestionar cachés, revisar permisos de archivos subidos y monitorizar los logs de errores.
- **Rollback:** Restaurar una versión anterior (archivos y base de datos) rápidamente en caso de un fallo crítico tras una actualización.

## 2. Herramientas de Despliegue Oficiales

Para transferir o actualizar código en el servidor, utiliza uno de los siguientes métodos según el entorno y las preferencias del usuario:

### A. Método con Git (Git Pull)
Ideal para servidores Linux o VPS con acceso SSH y Git instalado.
1. Accede por SSH al directorio del proyecto en el servidor (ej. `/var/www/miproyecto`).
2. Verifica el estado del repositorio (`git status`).
3. Realiza el despliegue ejecutando `git pull origin main` (o la rama de producción correspondiente).
4. Actualiza dependencias de la aplicación si aplica (ej. `composer install`).
5. Limpia cachés internas de la web.

### B. Método con FTP / SFTP
Ideal para entornos de hosting compartido, CPanel o cuando no se dispone de Git en el servidor.
1. Utiliza las credenciales de FTP/SFTP para acceder al directorio raíz web (usualmente `public_html`, `www`, o `/var/www/html/`).
2. Sube y sobrescribe **únicamente los archivos modificados** desde el entorno local al servidor remoto para agilizar la transferencia.
3. Para despliegues completos grandes, evalúa subir un archivo `.zip` del proyecto y descomprimirlo utilizando el administrador de archivos del panel de control (ej. CPanel) o vía terminal.

## 3. Flujo de Actualización Segura

Cuando el usuario solicite actualizar un sitio web en producción, sigue rigurosamente estos pasos:

1. **Notificación / Mantenimiento:** Para actualizaciones estructurales importantes, coloca un aviso temporal (ej. `maintenance.html`) y redirige el tráfico usando `.htaccess`.
2. **Backup Previo Crítico:**
   - **Base de datos:** Genera un volcado SQL del estado actual (`mysqldump -u user -p dbname > backup_pre_update.sql`).
   - **Archivos de configuración:** Respalda el archivo de conexión a la BD, `.env` y carpetas de contenido de usuarios (`uploads`, `images`).
3. **Despliegue de Código:** Ejecuta la transferencia de los nuevos archivos mediante **Git Pull** o **FTP/SFTP**.
4. **Migración de Base de Datos:** Si el update requiere nuevas tablas o columnas, ejecuta los scripts SQL proveídos para la actualización.
5. **Permisos Correctos:** Tras la subida, verifica que los archivos mantengan los permisos web estándar (archivos en `644`, directorios en `755`) para evitar el error *403 Forbidden*.
6. **Validación:** Comprueba que el sitio cargue correctamente en el navegador y no arroje *HTTP 500 Internal Server Error*.
7. **Limpieza:** Borra cachés del servidor y desactiva el modo mantenimiento.

## 4. Troubleshooting Web

- **Error HTTP 500 post-actualización:** Ocurre comúnmente por errores de sintaxis en PHP subido recientemente o reglas mal formadas en el `.htaccess`. Revisa inmediatamente el archivo `error_log` dentro de la carpeta afectada.
- **Cambios de diseño no visibles (CSS/JS):** Instruye al usuario a añadir parámetros de versión a sus archivos estáticos (ej. `estilos.css?v=2.0`) o a vaciar la caché de su navegador.
- **No se pueden subir imágenes:** Revisa los permisos de escritura del directorio de subida (debe poder ser escrito por el usuario del servidor web, como `www-data` o el usuario del CPanel).

## 5. Protocolo de Rollback (Plan de Contingencia)

Si la actualización provoca una rotura fatal e inmediata de la aplicación web:
1. Revierte el código subido:
   - *Si usaste Git:* `git reset --hard HEAD~1` o `git checkout <commit_seguro>`.
   - *Si usaste FTP:* Sube nuevamente el backup de los archivos de la versión anterior que reemplazaste.
2. Restaura la base de datos importando el volcado SQL generado en el Paso 2 (`mysql -u user -p dbname < backup_pre_update.sql`).
3. Verifica la restauración y procede a analizar la causa del fallo localmente (en entorno de desarrollo), sin experimentar en el servidor en vivo.
