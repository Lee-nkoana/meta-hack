# User profile and dashboard endpoint tests
import pytest


@pytest.mark.users
class TestUserProfile:
    """Tests for user profile endpoints"""
    
    def test_get_profile(self, client, auth_headers, test_user, test_user_data):
        """Test getting user profile"""
        response = client.get("/api/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "record_count" in data
        assert data["record_count"] == 0
    
    def test_get_profile_with_records(self, client, auth_headers, multiple_medical_records):
        """Test getting profile with record count"""
        response = client.get("/api/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["record_count"] == 5
    
    def test_get_profile_no_auth(self, client):
        """Test getting profile without authentication"""
        response = client.get("/api/users/me")
        
        assert response.status_code == 401
    
    def test_update_profile_email(self, client, auth_headers):
        """Test updating user email"""
        response = client.put(
            "/api/users/me",
            json={"email": "newemail@example.com"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "newemail@example.com"
    
    def test_update_profile_full_name(self, client, auth_headers):
        """Test updating user full name"""
        response = client.put(
            "/api/users/me",
            json={"full_name": "New Name"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["full_name"] == "New Name"
    
    def test_update_profile_password(self, client, auth_headers, test_user_data):
        """Test updating user password"""
        response = client.put(
            "/api/users/me",
            json={"password": "newpassword123"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify new password works
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["username"],
                "password": "newpassword123"
            }
        )
        assert login_response.status_code == 200
    
    def test_update_profile_duplicate_email(self, client, auth_headers, db_session):
        """Test updating to an already existing email"""
        # Create another user
        from app.models import User
        from app.utils.security import get_password_hash
        
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(other_user)
        db_session.commit()
        
        response = client.put(
            "/api/users/me",
            json={"email": "other@example.com"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_update_profile_no_auth(self, client):
        """Test updating profile without authentication"""
        response = client.put(
            "/api/users/me",
            json={"email": "new@example.com"}
        )
        
        assert response.status_code == 401


@pytest.mark.users
class TestDashboard:
    """Tests for dashboard endpoint"""
    
    def test_dashboard_no_records(self, client, auth_headers):
        """Test dashboard with no records"""
        response = client.get("/api/users/dashboard", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["total_records"] == 0
        assert data["records_with_translation"] == 0
        assert data["records_with_suggestions"] == 0
        assert data["recent_records"] == []
    
    def test_dashboard_with_records(self, client, auth_headers, multiple_medical_records):
        """Test dashboard with multiple records"""
        response = client.get("/api/users/dashboard", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["total_records"] == 5
        assert len(data["recent_records"]) == 5
    
    def test_dashboard_with_translations(self, client, auth_headers, test_medical_record, db_session):
        """Test dashboard counts records with translations"""
        test_medical_record.translated_text = "Translation here"
        test_medical_record.lifestyle_suggestions = "Suggestions here"
        db_session.commit()
        
        response = client.get("/api/users/dashboard", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["total_records"] == 1
        assert data["records_with_translation"] == 1
        assert data["records_with_suggestions"] == 1
    
    def test_dashboard_no_auth(self, client):
        """Test dashboard without authentication"""
        response = client.get("/api/users/dashboard")
        
        assert response.status_code == 401
