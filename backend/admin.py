import os
from datetime import datetime
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from passlib.context import CryptContext
from main import AdminUser, News, SiteSetting, ContactMessage, NewsletterSubscription, Testimonial, SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        db = SessionLocal()
        try:
            user = db.query(AdminUser).filter(AdminUser.username == username).first()
            if user and verify_password(password, user.password_hash) and user.is_active:
                request.session.update({"token": str(user.id), "rol": user.rol})
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


# --- Views ---

class AdminUserView(ModelView, model=AdminUser):
    column_list = [AdminUser.id, AdminUser.username, AdminUser.rol, AdminUser.is_active]
    form_columns = [AdminUser.username, AdminUser.password_hash, AdminUser.rol, AdminUser.is_active]
    column_searchable_list = [AdminUser.username]
    name_plural = "Usuarios Administradores"
    icon = "fa-solid fa-users"

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("rol") == "Editor"
    
    async def on_model_change(self, data, model, is_created, request):
        if 'password_hash' in data and not data['password_hash'].startswith("$2b$"):
            data['password_hash'] = get_password_hash(data['password_hash'])

class NewsView(ModelView, model=News):
    column_list = [News.id, News.titulo, News.seccion, News.estado, News.fecha_creacion, News.fecha_publicacion]
    form_columns = [News.titulo, News.copete, News.detalle, News.imagen_url, News.seccion, News.estado]
    column_searchable_list = [News.titulo, News.copete]
    form_choices = {
        'estado': [
            ('Borrador', 'Borrador'),
            ('Pendiente de Revisión', 'Pendiente de Revisión'),
            ('Publicado', 'Publicado'),
        ]
    }
    name_plural = "Noticias"
    icon = "fa-solid fa-newspaper"

    async def on_model_change(self, data, model, is_created, request):
        user_id = int(request.session.get("token"))
        rol = request.session.get("rol")
        
        if is_created:
            data['autor_id'] = user_id
        
        if data.get('estado') == 'Publicado':
            if rol != 'Editor':
                raise ValueError("Solo un Editor puede publicar noticias.")
            if not model.editor_id:
                data['editor_id'] = user_id
                data['fecha_publicacion'] = datetime.now()

class TestimonialView(ModelView, model=Testimonial):
    column_list = [Testimonial.id, Testimonial.cliente, Testimonial.empresa_puesto, Testimonial.estado, Testimonial.fecha_creacion, Testimonial.fecha_publicacion]
    form_columns = [Testimonial.cliente, Testimonial.empresa_puesto, Testimonial.comentario, Testimonial.estado]
    column_searchable_list = [Testimonial.cliente, Testimonial.comentario]
    form_choices = {
        'estado': [
            ('Borrador', 'Borrador'),
            ('Pendiente de Revisión', 'Pendiente de Revisión'),
            ('Publicado', 'Publicado'),
        ]
    }
    name_plural = "Testimonios / Clientes"
    icon = "fa-solid fa-comments"

    async def on_model_change(self, data, model, is_created, request):
        user_id = int(request.session.get("token"))
        rol = request.session.get("rol")
        
        if is_created:
            data['autor_id'] = user_id
        
        if data.get('estado') == 'Publicado':
            if rol != 'Editor':
                raise ValueError("Solo un Editor puede publicar testimonios.")
            if not model.editor_id:
                data['editor_id'] = user_id
                data['fecha_publicacion'] = datetime.now()

class SiteSettingView(ModelView, model=SiteSetting):
    column_list = [SiteSetting.clave, SiteSetting.valor, SiteSetting.descripcion]
    form_columns = [SiteSetting.clave, SiteSetting.valor, SiteSetting.descripcion]
    column_searchable_list = [SiteSetting.clave]
    name_plural = "Configuraciones"
    icon = "fa-solid fa-cogs"

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("rol") == "Editor"

class ContactMessageView(ModelView, model=ContactMessage):
    column_list = [ContactMessage.id, ContactMessage.nombre, ContactMessage.apellido, ContactMessage.email, ContactMessage.created_at, ContactMessage.status]
    can_create = False
    can_edit = True
    can_delete = False
    name_plural = "Prospectos (Contacto)"
    icon = "fa-solid fa-envelope"

class NewsletterSubscriptionView(ModelView, model=NewsletterSubscription):
    column_list = [NewsletterSubscription.id, NewsletterSubscription.email, NewsletterSubscription.created_at, NewsletterSubscription.active]
    can_create = False
    name_plural = "Suscripciones"
    icon = "fa-solid fa-rss"

def setup_admin(app, engine):
    authentication_backend = AdminAuth(secret_key="secret-key-12345")
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend, title="Aliso Web Admin")
    admin.add_view(NewsView)
    admin.add_view(TestimonialView)
    admin.add_view(ContactMessageView)
    admin.add_view(NewsletterSubscriptionView)
    admin.add_view(SiteSettingView)
    admin.add_view(AdminUserView)
