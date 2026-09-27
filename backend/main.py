"""
ALISO WEB SOLUTION — FastAPI Backend
Endpoints para formularios, contenidos dinámicos, soluciones verticales y panel de administración.
Base de datos: MySQL / MariaDB (AlisoWebDB) o SQLite para desarrollo/tests.
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func, Boolean, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# ── Logging ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aliso-backend")


# ══════════════════════════════
# SETTINGS
# ══════════════════════════════
class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:123456@localhost/AlisoWebDB"
    debug: bool = False
    app_name: str = "Aliso Web Solution API"
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# ══════════════════════════════
# DATABASE CONFIG
# ══════════════════════════════
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Dependency ──
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ══════════════════════════════
# MODELS
# ══════════════════════════════
class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    empresa = Column(String(200), nullable=True)
    servicio = Column(String(100), nullable=True)
    mensaje = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    status = Column(String(50), default="nuevo", nullable=False)  # nuevo, contactado, reunion_agendada, finalizado


class NewsletterSubscription(Base):
    __tablename__ = "newsletter_subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    active = Column(String(5), default="true", nullable=False)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default="Operador", nullable=False)  # 'Operador' o 'Editor'
    is_active = Column(Boolean, default=True)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    copete = Column(String(500), nullable=True)
    detalle = Column(Text, nullable=False)
    imagen_url = Column(String(255), nullable=True)
    seccion = Column(String(50), nullable=True)
    estado = Column(String(50), default="Borrador")  # Borrador, Pendiente de Revisión, Publicado
    autor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    editor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_publicacion = Column(DateTime, nullable=True)

    autor = relationship("AdminUser", foreign_keys=[autor_id])
    editor = relationship("AdminUser", foreign_keys=[editor_id])


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(String(500), nullable=True)
    descripcion = Column(String(255), nullable=True)


class Testimonial(Base):
    __tablename__ = "testimonials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente = Column(String(100), nullable=False)
    empresa_puesto = Column(String(150), nullable=True)
    comentario = Column(Text, nullable=False)
    estado = Column(String(50), default="Borrador")  # Borrador, Pendiente de Revisión, Publicado
    autor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    editor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_publicacion = Column(DateTime, nullable=True)

    autor = relationship("AdminUser", foreign_keys=[autor_id])
    editor = relationship("AdminUser", foreign_keys=[editor_id])


class VerticalApp(Base):
    """Aplicaciones verticales para clientes alojadas en subdominios."""
    __tablename__ = "vertical_apps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    categoria = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    subdominio_url = Column(String(255), nullable=False)
    icono = Column(String(50), default="⚡")
    badge = Column(String(50), default="Producción")
    orden = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


# ══════════════════════════════
# SCHEMAS (Pydantic v2)
# ══════════════════════════════
class ContactCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    empresa: Optional[str] = Field(None, max_length=200)
    servicio: Optional[str] = Field(None, max_length=100)
    mensaje: str = Field(..., min_length=10, max_length=5000)


class ContactResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    empresa: Optional[str]
    servicio: Optional[str]
    mensaje: str
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class NewsletterCreate(BaseModel):
    email: EmailStr


class NewsletterResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    active: str

    model_config = ConfigDict(from_attributes=True)


class VerticalAppResponse(BaseModel):
    id: int
    nombre: str
    slug: str
    categoria: str
    descripcion: str
    subdominio_url: str
    icono: str
    badge: str
    orden: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


# ══════════════════════════════
# LIFESPAN (FastAPI Moderno)
# ══════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Aliso Web API y verificando tablas en la base de datos...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas sincronizadas correctamente.")

        from admin import get_password_hash
        db = SessionLocal()
        try:
            # 1. Crear o actualizar usuario admin
            admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
            if not admin_user:
                logger.info("Creando usuario Administrador por defecto...")
                default_admin = AdminUser(
                    username="admin",
                    password_hash=get_password_hash("admin123"),
                    rol="Editor",
                    is_active=True
                )
                db.add(default_admin)
                db.commit()
                logger.info("✅ Administrador inicial creado.")
            else:
                # Asegurar que el hash use bcrypt nativo válido
                if not admin_user.password_hash.startswith("$2b$") and not admin_user.password_hash.startswith("$2a$"):
                    admin_user.password_hash = get_password_hash("admin123")
                    db.commit()
                    logger.info("✅ Contraseña de administrador actualizada a bcrypt nativo.")

            # 2. Poblar Parametría Inicial (site_settings)
            default_settings = [
                ("email_contacto", "solutions@aliso.com.ar", "Email corporativo principal"),
                ("telefono_contacto", "+54 9 381 472-0970", "Teléfono corporativo directo"),
                ("whatsapp_contacto", "+54 9 381 472-0970", "Línea WhatsApp Business"),
                ("direccion_contacto", "Buenos Aires & Tucumán, Argentina", "Sede corporativa y operaciones"),
                ("horario_atencion", "Lun – Vie, 09:00 – 18:30 (GMT-3)", "Horario de atención comercial"),
                ("linkedin_url", "https://www.linkedin.com/company/aliso-soluciones", "Perfil oficial en LinkedIn"),
                ("github_url", "https://github.com/aliso-soluciones", "Repositorio corporativo"),
            ]
            for clave, valor, desc in default_settings:
                existing = db.query(SiteSetting).filter(SiteSetting.clave == clave).first()
                if not existing:
                    db.add(SiteSetting(clave=clave, valor=valor, descripcion=desc))
            db.commit()
            logger.info("✅ Parametría inicial verificada.")

            # 3. Poblar Soluciones Verticales iniciales si está vacío
            if db.query(VerticalApp).count() == 0:
                apps = [
                    VerticalApp(
                        nombre="Aliso Salud & Sanatorio",
                        slug="salud",
                        categoria="Salud & Clínicas",
                        descripcion="Plataforma web integral para gestión de internación, historias clínicas y nomenclador sanatorial en tiempo real.",
                        subdominio_url="https://salud.aliso.com.ar",
                        icono="🏥",
                        badge="Producción",
                        orden=1,
                        is_active=True
                    ),
                    VerticalApp(
                        nombre="Aliso Balance & Media TV",
                        slug="balance-tv",
                        categoria="Medios & Telecomunicaciones",
                        descripcion="Sistema de monitoreo, telemetría y balance de señales audiovisuales y streaming corporativo.",
                        subdominio_url="https://balance.aliso.com.ar",
                        icono="📺",
                        badge="Producción",
                        orden=2,
                        is_active=True
                    ),
                    VerticalApp(
                        nombre="Aliso Facturación & Aranceles",
                        slug="facturacion",
                        categoria="Gestión & ERP",
                        descripcion="Motor inteligente de liquidación de aranceles médicos, validación de convenios y comprobantes electrónicos.",
                        subdominio_url="https://facturacion.aliso.com.ar",
                        icono="📑",
                        badge="Acceso Clientes",
                        orden=3,
                        is_active=True
                    ),
                    VerticalApp(
                        nombre="Aliso Laboratorio & Diagnóstico",
                        slug="laboratorio",
                        categoria="Bioanálisis & Diagnóstico",
                        descripcion="Portal de trazabilidad de muestras biológicas, auto-analizadores y emisión segura de protocolos digitales.",
                        subdominio_url="https://laboratorio.aliso.com.ar",
                        icono="🔬",
                        badge="Beta Privada",
                        orden=4,
                        is_active=True
                    )
                ]
                db.add_all(apps)
                db.commit()
                logger.info("✅ Soluciones verticales iniciales creadas.")

        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Aviso durante la inicialización de base de datos: {e}")
    yield
    logger.info("Cerrando recursos de la API...")


# ══════════════════════════════
# APP INSTANCE
# ══════════════════════════════
app = FastAPI(
    title=settings.app_name,
    description="Backend API corporativo para el sitio web de Aliso – Consultoría GeneXus & IA",
    version="1.3.0",
    lifespan=lifespan,
)

# ── CORS ──
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if not origins or origins == ["*"]:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SessionMiddleware es manejado directamente por SQLAdmin en setup_admin

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Setup Admin Panel ──
from admin import setup_admin
setup_admin(app, engine)


# ══════════════════════════════
# ENDPOINTS
# ══════════════════════════════

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Verificar estado del servidor y conexión a la DB."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.warning(f"Health check DB warning: {e}")
        db_status = "disconnected"
    return HealthResponse(
        status="ok",
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )


@app.post("/api/contact", response_model=ContactResponse, status_code=201, tags=["Contact"])
def create_contact_message(data: ContactCreate, db: Session = Depends(get_db)):
    """Recibir un mensaje del formulario de contacto o solicitud de reunión."""
    logger.info(f"📩 Nuevo contacto: {data.nombre} {data.apellido} <{data.email}> [{data.servicio}]")
    msg = ContactMessage(
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        empresa=data.empresa,
        servicio=data.servicio,
        mensaje=data.mensaje,
        status="nuevo"
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    logger.info(f"✅ Mensaje #{msg.id} guardado correctamente.")
    return msg


@app.get("/api/contact", response_model=list[ContactResponse], tags=["Contact"])
def list_contact_messages(db: Session = Depends(get_db)):
    """Listar todos los mensajes de contacto (admin)."""
    return db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()


@app.post("/api/newsletter", response_model=NewsletterResponse, status_code=201, tags=["Newsletter"])
def subscribe_newsletter(data: NewsletterCreate, db: Session = Depends(get_db)):
    """Suscribirse al newsletter corporativo."""
    existing = db.query(NewsletterSubscription).filter_by(email=data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Este email ya está suscrito.")
    sub = NewsletterSubscription(email=data.email)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    logger.info(f"📬 Nueva suscripción: {data.email}")
    return sub


@app.get("/api/newsletter", response_model=list[NewsletterResponse], tags=["Newsletter"])
def list_newsletter_subscriptions(db: Session = Depends(get_db)):
    """Listar suscripciones al newsletter (admin)."""
    return db.query(NewsletterSubscription).order_by(NewsletterSubscription.created_at.desc()).all()


@app.get("/api/vertical-apps", response_model=list[VerticalAppResponse], tags=["VerticalApps"])
def list_vertical_apps(db: Session = Depends(get_db)):
    """Listar aplicaciones web verticales activas para clientes de Aliso."""
    return db.query(VerticalApp).filter(VerticalApp.is_active == True).order_by(VerticalApp.orden.asc()).all()


@app.get("/api/news", tags=["News"])
def list_published_news(db: Session = Depends(get_db)):
    """Obtener todas las noticias publicadas para mostrar en el frontend."""
    news = db.query(News).filter(News.estado == 'Publicado').order_by(News.fecha_publicacion.desc()).all()
    return [{
        "id": n.id,
        "titulo": n.titulo,
        "copete": n.copete,
        "detalle": n.detalle,
        "imagen_url": n.imagen_url,
        "seccion": n.seccion,
        "fecha_publicacion": n.fecha_publicacion
    } for n in news]


@app.get("/api/testimonials", tags=["Testimonials"])
def list_published_testimonials(db: Session = Depends(get_db)):
    """Obtener todas las recomendaciones/experiencias publicadas para el frontend."""
    testimonials = db.query(Testimonial).filter(Testimonial.estado == 'Publicado').order_by(Testimonial.fecha_publicacion.desc()).all()
    return [{
        "id": t.id,
        "cliente": t.cliente,
        "empresa_puesto": t.empresa_puesto,
        "comentario": t.comentario,
        "fecha_publicacion": t.fecha_publicacion
    } for t in testimonials]


@app.get("/api/settings", tags=["Settings"])
def get_site_settings(db: Session = Depends(get_db)):
    """Obtener todas las configuraciones públicas del sitio (tel, mail, dirección, etc.)."""
    settings_list = db.query(SiteSetting).all()
    return {s.clave: s.valor for s in settings_list}


@app.get("/", tags=["Root"])
def root():
    return {"message": "Aliso Web Solution API v1.3.0", "docs": "/docs", "admin": "/admin"}

