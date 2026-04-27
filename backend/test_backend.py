import pytest
from fastapi.testclient import TestClient
from main import app, Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Setup test database (SQLite for simplicity in tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine_test = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
    engine_test.dispose() # Close all connections
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except PermissionError:
            pass # Ignore if still locked on Windows

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_contact_message():
    payload = {
        "nombre": "Test",
        "apellido": "User",
        "email": "test@aliso.com.ar",
        "empresa": "Aliso Corp",
        "servicio": "consultoria",
        "mensaje": "Este es un mensaje de prueba profesional para validación."
    }
    response = client.post("/api/contact", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Test"
    assert data["email"] == "test@aliso.com.ar"
    assert "id" in data

def test_contact_validation_error():
    # Short message
    payload = {
        "nombre": "T",
        "apellido": "U",
        "email": "not-an-email",
        "mensaje": "Short"
    }
    response = client.post("/api/contact", json=payload)
    assert response.status_code == 422

def test_newsletter_subscription():
    payload = {"email": "newsletter@test.com"}
    response = client.post("/api/newsletter", json=payload)
    assert response.status_code == 201
    
    # Duplicate
    response = client.post("/api/newsletter", json=payload)
    assert response.status_code == 409
