import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db, Base
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Plant Delivery API" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_user_registration(setup_database):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_user_login(setup_database):
    # First register a user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint(setup_database):
    # Try to access protected endpoint without token
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_plants_list():
    response = client.get("/api/v1/plants/")
    assert response.status_code == 200
    assert "plants" in response.json()

def test_admin_endpoints_protected():
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401
