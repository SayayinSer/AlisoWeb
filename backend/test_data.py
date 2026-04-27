import sys
import os
from main import SessionLocal, News, SiteSetting, AdminUser
from datetime import datetime

db = SessionLocal()

# Add SiteSetting
setting = db.query(SiteSetting).filter_by(clave="telefono_contacto").first()
if not setting:
    setting = SiteSetting(clave="telefono_contacto", valor="+1234567890", descripcion="Teléfono principal")
    db.add(setting)

# Add News
user = db.query(AdminUser).first()
if user:
    news = db.query(News).filter_by(titulo="Lanzamiento de Nueva Web").first()
    if not news:
        news = News(
            titulo="Lanzamiento de Nueva Web",
            copete="Estamos orgullosos de presentar nuestro nuevo sitio web.",
            detalle="Este sitio ha sido renovado con lo último en tecnología LAMP, FastAPI y diseño dinámico.",
            seccion="Novedades",
            estado="Publicado",
            autor_id=user.id,
            editor_id=user.id,
            fecha_publicacion=datetime.now()
        )
        db.add(news)

db.commit()
db.close()
print("Datos de prueba insertados exitosamente.")
