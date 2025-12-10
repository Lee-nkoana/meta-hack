# Test configuration and fixtures
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import create_app
from app.database import Base, SessionLocal
from app.models import User, MedicalRecord
from app.utils.security import get_password_hash

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def app(test_db):
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_URL'] = SQLALCHEMY_TEST_DATABASE_URL
    
    # Patch the database session to use test database
    from app import database
    original_session = database.SessionLocal
    database.SessionLocal = TestingSessionLocal
    
    yield app
    
    # Restore original session
    database.SessionLocal = original_session


@pytest.fixture(scope="function")
def client(app):
    """Create test client with Flask app"""
    return app.test_client()


@pytest.fixture(scope="function")
def app_context(app):
    """Create app context for tests"""
    with app.app_context():
        yield


@pytest.fixture(scope="function")
def db_session(test_db, app_context):
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
def auth_headers(client, test_user, test_user_data, app_context):
    """Get authentication headers with JWT token"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    token = response.get_json()["access_token"]
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
    from datetime import datetime, timezone
    record = MedicalRecord(
        user_id=test_user.id,
        title=test_medical_record_data["title"],
        original_text=test_medical_record_data["original_text"],
        record_type=test_medical_record_data["record_type"],
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


@pytest.fixture
def multiple_medical_records(db_session, test_user):
    """Create multiple test medical records"""
    from datetime import datetime, timezone
    records = [
        MedicalRecord(
            user_id=test_user.id,
            title=f"Record {i}",
            original_text=f"Test content {i}",
            record_type="doctor_note",
            created_at=datetime.now(timezone.utc)
        )
        for i in range(5)
    ]
    for record in records:
        db_session.add(record)
    db_session.commit()
    return records
