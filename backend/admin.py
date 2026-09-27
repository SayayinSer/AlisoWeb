import os
from datetime import datetime
import bcrypt
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from main import (
    AdminUser, News, SiteSetting, ContactMessage,
    NewsletterSubscription, Testimonial, VerticalApp, SessionLocal
)

# ── Manejo de contraseñas con bcrypt nativo (sin dependencias obsoletas) ──
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        db = SessionLocal()
        try:
            user = db.query(AdminUser).filter(AdminUser.username == username).first()
            if user and user.is_active and verify_password(password, user.password_hash):
                request.session.update({"token": str(user.id), "rol": user.rol, "username": user.username})
                return True
        finally:
            db.close()
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        
        db = SessionLocal()
        try:
            user = db.query(AdminUser).filter(AdminUser.id == int(token)).first()
            if not user or not user.is_active:
                return False
        except Exception:
            return False
        finally:
            db.close()
        return True


# ══════════════════════════════════════════════════════════════════════════════
# VISTAS DEL PANEL DE ADMINISTRACIÓN
# ══════════════════════════════════════════════════════════════════════════════

class ContactMessageView(ModelView, model=ContactMessage):
    """Gestión de prospectos, reuniones agendadas y consultas web."""
    column_list = [
        ContactMessage.id,
        ContactMessage.nombre,
        ContactMessage.apellido,
        ContactMessage.email,
        ContactMessage.empresa,
        ContactMessage.servicio,
        ContactMessage.status,
        ContactMessage.created_at,
    ]
    column_searchable_list = [
        ContactMessage.nombre,
        ContactMessage.apellido,
        ContactMessage.email,
        ContactMessage.empresa,
        ContactMessage.servicio,
    ]
    column_sortable_list = [
        ContactMessage.id,
        ContactMessage.created_at,
        ContactMessage.status,
        ContactMessage.servicio,
    ]
    column_default_sort = [(ContactMessage.created_at, True)]
    form_choices = {
        'status': [
            ('nuevo', 'Nuevo (Sin contactar)'),
            ('contactado', 'Contactado en proceso'),
            ('reunion_agendada', 'Reunión Agendada'),
            ('finalizado', 'Finalizado / Cerrado'),
        ]
    }
    can_create = False
    can_edit = True
    can_delete = True
    name = "Reunión / Prospecto"
    name_plural = "Reuniones & Prospectos"
    icon = "fa-solid fa-calendar-check"


class NewsletterSubscriptionView(ModelView, model=NewsletterSubscription):
    """Mails registrados para el newsletter corporativo."""
    column_list = [
        NewsletterSubscription.id,
        NewsletterSubscription.email,
        NewsletterSubscription.created_at,
        NewsletterSubscription.active,
    ]
    column_searchable_list = [NewsletterSubscription.email]
    column_sortable_list = [NewsletterSubscription.id, NewsletterSubscription.created_at]
    column_default_sort = [(NewsletterSubscription.created_at, True)]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Suscripción"
    name_plural = "Mails Registrados (Newsletter)"
    icon = "fa-solid fa-envelope-open-text"


class SiteSettingView(ModelView, model=SiteSetting):
    """Parametría total del sitio (teléfonos, emails, dirección, horarios, redes)."""
    column_list = [SiteSetting.clave, SiteSetting.valor, SiteSetting.descripcion]
    form_columns = [SiteSetting.clave, SiteSetting.valor, SiteSetting.descripcion]
    column_searchable_list = [SiteSetting.clave, SiteSetting.descripcion]
    column_sortable_list = [SiteSetting.clave]
    name = "Parámetro"
    name_plural = "Parametría del Sitio"
    icon = "fa-solid fa-sliders"

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("rol") == "Editor"


class VerticalAppView(ModelView, model=VerticalApp):
    """Aplicaciones web verticales por industria alojadas en subdominios."""
    column_list = [
        VerticalApp.id,
        VerticalApp.nombre,
        VerticalApp.categoria,
        VerticalApp.subdominio_url,
        VerticalApp.badge,
        VerticalApp.orden,
        VerticalApp.is_active,
    ]
    form_columns = [
        VerticalApp.nombre,
        VerticalApp.slug,
        VerticalApp.categoria,
        VerticalApp.descripcion,
        VerticalApp.subdominio_url,
        VerticalApp.icono,
        VerticalApp.badge,
        VerticalApp.orden,
        VerticalApp.is_active,
    ]
    column_searchable_list = [VerticalApp.nombre, VerticalApp.categoria, VerticalApp.subdominio_url]
    column_sortable_list = [VerticalApp.orden, VerticalApp.nombre, VerticalApp.categoria]
    column_default_sort = [(VerticalApp.orden, False)]
    form_choices = {
        'badge': [
            ('Producción', 'En Producción'),
            ('Acceso Clientes', 'Acceso Clientes'),
            ('Beta Privada', 'Beta Privada'),
            ('Próximamente', 'Próximamente'),
        ]
    }
    name = "Solución Vertical"
    name_plural = "Soluciones Verticales (Subdominios)"
    icon = "fa-solid fa-cubes"


class NewsView(ModelView, model=News):
    """Noticias y artículos de innovación técnica."""
    column_list = [News.id, News.titulo, News.seccion, News.estado, News.fecha_creacion, News.fecha_publicacion]
    form_columns = [News.titulo, News.copete, News.detalle, News.imagen_url, News.seccion, News.estado]
    column_searchable_list = [News.titulo, News.copete]
    column_sortable_list = [News.id, News.fecha_creacion, News.fecha_publicacion]
    column_default_sort = [(News.fecha_creacion, True)]
    form_choices = {
        'estado': [
            ('Borrador', 'Borrador'),
            ('Pendiente de Revisión', 'Pendiente de Revisión'),
            ('Publicado', 'Publicado'),
        ]
    }
    name = "Noticia"
    name_plural = "Noticias & Artículos"
    icon = "fa-solid fa-newspaper"

    async def on_model_change(self, data, model, is_created, request):
        user_id = int(request.session.get("token", 1))
        rol = request.session.get("rol", "Editor")
        
        if is_created:
            data['autor_id'] = user_id
        
        if data.get('estado') == 'Publicado':
            if rol != 'Editor':
                raise ValueError("Solo un Editor puede publicar noticias.")
            if not getattr(model, 'editor_id', None):
                data['editor_id'] = user_id
                data['fecha_publicacion'] = datetime.now()


class TestimonialView(ModelView, model=Testimonial):
    """Testimonios y experiencias de clientes."""
    column_list = [Testimonial.id, Testimonial.cliente, Testimonial.empresa_puesto, Testimonial.estado, Testimonial.fecha_creacion]
    form_columns = [Testimonial.cliente, Testimonial.empresa_puesto, Testimonial.comentario, Testimonial.estado]
    column_searchable_list = [Testimonial.cliente, Testimonial.comentario]
    column_sortable_list = [Testimonial.id, Testimonial.fecha_creacion]
    column_default_sort = [(Testimonial.fecha_creacion, True)]
    form_choices = {
        'estado': [
            ('Borrador', 'Borrador'),
            ('Pendiente de Revisión', 'Pendiente de Revisión'),
            ('Publicado', 'Publicado'),
        ]
    }
    name = "Testimonio"
    name_plural = "Testimonios de Clientes"
    icon = "fa-solid fa-comments"

    async def on_model_change(self, data, model, is_created, request):
        user_id = int(request.session.get("token", 1))
        rol = request.session.get("rol", "Editor")
        
        if is_created:
            data['autor_id'] = user_id
        
        if data.get('estado') == 'Publicado':
            if rol != 'Editor':
                raise ValueError("Solo un Editor puede publicar testimonios.")
            if not getattr(model, 'editor_id', None):
                data['editor_id'] = user_id
                data['fecha_publicacion'] = datetime.now()


class AdminUserView(ModelView, model=AdminUser):
    """Gestión de usuarios y accesos al panel administrativo."""
    column_list = [AdminUser.id, AdminUser.username, AdminUser.rol, AdminUser.is_active]
    form_columns = [AdminUser.username, AdminUser.password_hash, AdminUser.rol, AdminUser.is_active]
    column_searchable_list = [AdminUser.username]
    name = "Usuario"
    name_plural = "Usuarios Administradores"
    icon = "fa-solid fa-user-shield"

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("rol") == "Editor"
    
    async def on_model_change(self, data, model, is_created, request):
        if 'password_hash' in data and not data['password_hash'].startswith("$2b$"):
            data['password_hash'] = get_password_hash(data['password_hash'])


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRO DEL PANEL SQLADMIN
# ══════════════════════════════════════════════════════════════════════════════
def setup_admin(app, engine):
    authentication_backend = AdminAuth(secret_key="aliso-super-secret-admin-session-2026")
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend, title="Aliso Web Admin — Gestión Integral")
    
    # 1. Módulos Operativos y Prospectos
    admin.add_view(ContactMessageView)
    admin.add_view(NewsletterSubscriptionView)
    
    # 2. Soluciones Verticales & Subdominios
    admin.add_view(VerticalAppView)
    
    # 3. Parametría y Configuración
    admin.add_view(SiteSettingView)
    
    # 4. Contenidos Públicos
    admin.add_view(NewsView)
    admin.add_view(TestimonialView)
    
    # 5. Seguridad y Usuarios
    admin.add_view(AdminUserView)

