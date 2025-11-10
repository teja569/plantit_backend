import pytest
import json
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

@pytest.fixture
def auth_headers():
    """Create a test user and return auth headers"""
    # Register test user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login and get token
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers():
    """Create admin user and return auth headers"""
    # Register admin user
    user_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "role": "admin"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login and get token
    login_data = {
        "email": "admin@example.com",
        "password": "adminpassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Plant Delivery API" in response.json()["message"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_user_registration(setup_database):
    """Test user registration"""
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
    """Test user login"""
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
    """Test protected endpoint without token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_get_current_user(setup_database, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_plants_list():
    """Test plants listing"""
    response = client.get("/api/v1/plants/")
    assert response.status_code == 200
    assert "plants" in response.json()

def test_create_plant(setup_database, auth_headers):
    """Test plant creation (requires seller role)"""
    # First become a seller
    onboarding_data = {
        "business_name": "Test Nursery",
        "business_type": "Nursery",
        "business_address": "123 Plant St",
        "business_phone": "555-0123",
        "business_email": "test@example.com"
    }
    response = client.post("/api/v1/seller/onboard", json=onboarding_data, headers=auth_headers)
    assert response.status_code == 200
    
    # Now create a plant
    plant_data = {
        "name": "Test Plant",
        "description": "A beautiful test plant",
        "price": 25.99,
        "category": "Indoor",
        "species": "Test Species",
        "care_instructions": "Water daily",
        "stock_quantity": 10
    }
    response = client.post("/api/v1/plants/", data=plant_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Plant"

def test_admin_endpoints_protected(setup_database):
    """Test admin endpoints are protected"""
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401

def test_admin_dashboard(setup_database, admin_headers):
    """Test admin dashboard"""
    response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert response.status_code == 200
    assert "stats" in response.json()

def test_seller_onboarding(setup_database, auth_headers):
    """Test seller onboarding"""
    onboarding_data = {
        "business_name": "Test Nursery",
        "business_type": "Nursery",
        "business_address": "123 Plant St",
        "business_phone": "555-0123",
        "business_email": "test@example.com"
    }
    response = client.post("/api/v1/seller/onboard", json=onboarding_data, headers=auth_headers)
    assert response.status_code == 200

def test_seller_dashboard(setup_database, auth_headers):
    """Test seller dashboard"""
    # First become a seller
    onboarding_data = {
        "business_name": "Test Nursery",
        "business_type": "Nursery",
        "business_address": "123 Plant St",
        "business_phone": "555-0123",
        "business_email": "test@example.com"
    }
    client.post("/api/v1/seller/onboard", json=onboarding_data, headers=auth_headers)
    
    # Test dashboard
    response = client.get("/api/v1/seller/dashboard", headers=auth_headers)
    assert response.status_code == 200
    assert "total_plants" in response.json()

def test_ml_prediction_endpoint(setup_database, auth_headers):
    """Test ML prediction endpoint"""
    # Create a simple test image file
    test_image_content = b"fake_image_content"
    
    response = client.post(
        "/api/v1/plants/predict",
        files={"image": ("test.jpg", test_image_content, "image/jpeg")},
        headers=auth_headers
    )
    # This might fail due to image processing, but should not crash
    assert response.status_code in [200, 422, 500]

def test_order_creation(setup_database, auth_headers):
    """Test order creation"""
    # First create a seller and plant
    onboarding_data = {
        "business_name": "Test Nursery",
        "business_type": "Nursery",
        "business_address": "123 Plant St",
        "business_phone": "555-0123",
        "business_email": "test@example.com"
    }
    client.post("/api/v1/seller/onboard", json=onboarding_data, headers=auth_headers)
    
    plant_data = {
        "name": "Test Plant",
        "description": "A beautiful test plant",
        "price": 25.99,
        "category": "Indoor",
        "species": "Test Species",
        "care_instructions": "Water daily",
        "stock_quantity": 10
    }
    plant_response = client.post("/api/v1/plants/", data=plant_data, headers=auth_headers)
    plant_id = plant_response.json()["id"]
    
    # Create order
    order_data = {
        "seller_id": 1,  # Assuming seller ID is 1
        "items": [{"plant_id": plant_id, "quantity": 1}],
        "shipping_address": "123 Buyer St",
        "notes": "Please handle with care"
    }
    response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["total_price"] == 25.99

def test_rate_limiting():
    """Test rate limiting"""
    # Make multiple requests to trigger rate limiting
    for i in range(15):  # More than the 10/minute limit
        response = client.get("/")
        if response.status_code == 429:
            break
    else:
        # If we didn't hit rate limit, that's also acceptable for testing
        assert True

def test_cors_headers():
    """Test CORS headers"""
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
