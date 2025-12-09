# Test configuration and fixtures
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, MedicalRecord
from app.utils.security import get_password_hash

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session(test_db):
    """Get database session for direct database access in tests"""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user_data():
    """Test user registration data"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user in the database"""
    user = User(
        email=test_user_data["email"],
        username=test_user_data["username"],
        hashed_password=get_password_hash(test_user_data["password"]),
        full_name=test_user_data["full_name"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user, test_user_data):
    """Get authentication headers with JWT token"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_medical_record_data():
    """Test medical record data"""
    return {
        "title": "Blood Test Results",
        "original_text": "WBC: 7.5, RBC: 4.8, HGB: 14.2, PLT: 250",
        "record_type": "lab_result"
    }


@pytest.fixture
def test_medical_record(db_session, test_user, test_medical_record_data):
    """Create a test medical record in the database"""
    record = MedicalRecord(
        user_id=test_user.id,
        title=test_medical_record_data["title"],
        original_text=test_medical_record_data["original_text"],
        record_type=test_medical_record_data["record_type"]
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


@pytest.fixture
def multiple_medical_records(db_session, test_user):
    """Create multiple test medical records"""
    records = [
        MedicalRecord(
            user_id=test_user.id,
            title=f"Record {i}",
            original_text=f"Test content {i}",
            record_type="doctor_note"
        )
        for i in range(5)
    ]
    for record in records:
        db_session.add(record)
    db_session.commit()
    return records
