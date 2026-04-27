import sys
import os

# Asegurar que el directorio actual esté en el PATH
INTERP = os.path.expanduser("~/virtualenv/backend/3.10/bin/python") # Ruta típica cPanel, se ignora usualmente pero es buena práctica
if sys.executable != INTERP:
    pass

sys.path.insert(0, os.path.dirname(__file__))

# Importamos el adaptador WSGI a ASGI
from a2wsgi import ASGIMiddleware

# Importamos la aplicación FastAPI
from main import app

# Creamos la aplicación WSGI requerida por Passenger (cPanel)
application = ASGIMiddleware(app)
