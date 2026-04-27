"""
Script para crear la base de datos AlisoWebDB en MySQL.
Ejecutar una sola vez antes de iniciar el backend.
"""
from sqlalchemy import create_engine, text

# Conexión al servidor MySQL (sin especificar base de datos)
MYSQL_URL = "mysql+pymysql://root:123456@localhost/"

engine = create_engine(MYSQL_URL, isolation_level="AUTOCOMMIT")

with engine.connect() as conn:
    # Check if database exists
    result = conn.execute(text("SHOW DATABASES LIKE 'AlisoWebDB'"))
    exists = result.fetchone()
    if not exists:
        conn.execute(text("CREATE DATABASE `AlisoWebDB` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        print("[OK] Base de datos 'AlisoWebDB' creada exitosamente en MySQL.")
    else:
        print("[INFO] La base de datos 'AlisoWebDB' ya existe en MySQL.")

engine.dispose()
