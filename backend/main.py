"""
ALISO WEB SOLUTION — FastAPI Backend
Endpoints para formularios y datos del sitio web.
Base de datos: PostgreSQL (AlisoWebDB)
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from datetime import datetime
from typing import Optional
import logging

# ── Logging ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aliso-backend")

from pydantic_settings import BaseSettings, SettingsConfigDict

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
engine = create_engine(settings.database_url, echo=settings.debug, pool_pre_ping=True)
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
    status = Column(String(20), default="nuevo", nullable=False)


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
    rol = Column(String(20), default="Operador", nullable=False) # 'Operador' or 'Editor'
    is_active = Column(Boolean, default=True)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    copete = Column(String(500), nullable=True)
    detalle = Column(Text, nullable=False)
    imagen_url = Column(String(255), nullable=True)
    seccion = Column(String(50), nullable=True)
    estado = Column(String(50), default="Borrador") # Borrador, Pendiente de Revisión, Publicado
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
    estado = Column(String(50), default="Borrador") # Borrador, Pendiente de Revisión, Publicado
    autor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    editor_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_publicacion = Column(DateTime, nullable=True)

    autor = relationship("AdminUser", foreign_keys=[autor_id])
    editor = relationship("AdminUser", foreign_keys=[editor_id])


# ══════════════════════════════
# SCHEMAS (Pydantic)
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

    class Config:
        from_attributes = True


class NewsletterCreate(BaseModel):
    email: EmailStr


class NewsletterResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    active: str

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


# ══════════════════════════════
# APP INSTANCE
# ══════════════════════════════
app = FastAPI(
    title=settings.app_name,
    description="Backend API corporativo para el sitio web de Aliso – Consultoría GeneXus & IA",
    version="1.1.0",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="super-secret-key-12345")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Initialize Admin
from admin import setup_admin, get_password_hash
setup_admin(app, engine)

# ── Startup: create tables and init admin ──
@app.on_event("startup")
def on_startup():
    logger.info("Creando tablas en la base de datos AlisoWebDB...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tablas creadas correctamente.")
    
    # Create default AdminUser if none exists
    db = SessionLocal()
    try:
        if db.query(AdminUser).count() == 0:
            logger.info("Creando usuario Editor por defecto...")
            default_admin = AdminUser(
                username="admin",
                password_hash=get_password_hash("admin123"),
                rol="Editor"
            )
            db.add(default_admin)
            db.commit()
    finally:
        db.close()


# ══════════════════════════════
# ENDPOINTS
# ══════════════════════════════

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Verificar estado del servidor y conexión a la DB."""
    try:
        db.execute(db.bind.dialect.statement_compiler(db.bind.dialect, None).__class__.__module__ and "SELECT 1" or "SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return HealthResponse(
        status="ok",
        database=db_status,
        timestamp=datetime.utcnow(),
    )


@app.post("/api/contact", response_model=ContactResponse, status_code=201, tags=["Contact"])
def create_contact_message(data: ContactCreate, db: Session = Depends(get_db)):
    """Recibir un mensaje del formulario de contacto."""
    logger.info(f"📩 Nuevo contacto: {data.nombre} {data.apellido} <{data.email}>")
    msg = ContactMessage(
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        empresa=data.empresa,
        servicio=data.servicio,
        mensaje=data.mensaje,
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
    """Suscribirse al newsletter."""
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


@app.get("/api/news", tags=["News"])
def list_published_news(db: Session = Depends(get_db)):
    """Obtener todas las noticias publicadas para mostrar en el frontend."""
    news = db.query(News).filter(News.estado == 'Publicado').order_by(News.fecha_publicacion.desc()).all()
    # Simple dict response since we didn't define a Pydantic schema for this
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
    """Obtener todas las configuraciones públicas del sitio."""
    settings_list = db.query(SiteSetting).all()
    return {s.clave: s.valor for s in settings_list}


@app.get("/", tags=["Root"])
def root():
    return {"message": "Aliso Web Solution API v1.1.0", "docs": "/docs"}
