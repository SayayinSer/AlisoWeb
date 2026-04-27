# Guía de Despliegue en cPanel (Hosting Compartido)

Esta guía explica cómo subir y configurar el proyecto AlisoWeb en un entorno de Hosting Compartido con cPanel que soporta aplicaciones Python.

## Paso 1: Preparar los archivos localmente
1. Haz doble clic en el archivo `preparar_produccion.bat`.
2. Esto creará una carpeta llamada `dist_produccion` con dos subcarpetas:
   - `public_html`: Contiene tu Frontend (HTML, CSS, JS, Imágenes).
   - `backend`: Contiene tu API en FastAPI.

## Paso 2: Subir archivos a cPanel
1. Ingresa a tu cPanel y ve al **Administrador de Archivos (File Manager)**.
2. Sube el contenido de la carpeta local `dist_produccion/public_html` directamente a la carpeta `public_html` (o la raíz de tu dominio) de tu servidor cPanel.
3. En la raíz de tu servidor (un nivel antes de `public_html`, por ejemplo en `/home/tu_usuario/`), crea una carpeta llamada `alisoweb_backend`.
4. Sube todo el contenido de la carpeta local `dist_produccion/backend` dentro de la nueva carpeta `alisoweb_backend`.

## Paso 3: Base de Datos MySQL
1. En cPanel, ve a **Bases de datos MySQL**.
2. Crea una base de datos nueva (ej. `tuusuario_alisowebdb`).
3. Crea un usuario (ej. `tuusuario_admin`) y asígnale una contraseña segura.
4. Vincula el usuario a la base de datos con **Todos los privilegios**.
5. Abre el archivo `.env` que subiste dentro de `alisoweb_backend` y actualiza la variable `DATABASE_URL`:
   `DATABASE_URL="mysql+pymysql://tuusuario_admin:tu_password@localhost/tuusuario_alisowebdb"`

## Paso 4: Configurar la App Python en cPanel
1. En cPanel, busca la herramienta **"Setup Python App"** (Configurar Aplicación Python).
2. Haz clic en **Create Application**:
   - **Python version:** Recomendada 3.10 o superior.
   - **Application root:** Escribe el nombre de la carpeta backend: `alisoweb_backend`.
   - **Application URL:** Escribe `/api` (esto hará que la API responda en `tudominio.com/api`).
   - **Application startup file:** Escribe `passenger_wsgi.py`.
   - **Application Entry point:** Escribe `application`.
3. Dale a **Crear (Create)**.
4. Una vez creada, en la misma pantalla verás una sección de "Configuration files" o comandos para ejecutar. 
5. Si ves una caja de texto que dice "Run pip install", escribe `requirements.txt` y dale click a **Add** e instálalos allí mismo (el botón "Run pip install").

## Paso 5: Creación de tablas
Dado que el servidor no correrá automáticamente el evento startup para crear tablas si se usa a través de Passenger en algunas configuraciones:
- Si tu hosting provee terminal SSH, conéctate, entra al entorno virtual de la app y corre `python create_db.py` seguido de `python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"`.
- O alternativamente, antes de subir, exporta tu base de datos local a SQL e impórtala vía **phpMyAdmin** en cPanel.

## ¡Listo!
Ahora tu sitio principal responderá en `tudominio.com` sirviendo el HTML estático, y cualquier llamada a `tudominio.com/api/...` será procesada por tu aplicación FastAPI de Python.
