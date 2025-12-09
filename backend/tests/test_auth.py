# Authentication endpoint tests
import pytest


@pytest.mark.auth
class TestUserRegistration:
    """Tests for user registration endpoint"""
    
    def test_register_new_user(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_username(self, client, test_user, test_user_data):
        """Test registration with existing username"""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client, test_user, test_user_data):
        """Test registration with existing email"""
        new_user = test_user_data.copy()
        new_user["username"] = "differentuser"
        response = client.post("/api/auth/register", json=new_user)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client, test_user_data):
        """Test registration with invalid email format"""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "not-an-email"
        response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_register_short_password(self, client, test_user_data):
        """Test registration with password too short"""
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "12345"
        response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_register_short_username(self, client, test_user_data):
        """Test registration with username too short"""
        invalid_data = test_user_data.copy()
        invalid_data["username"] = "ab"
        response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422


@pytest.mark.auth
class TestUserLogin:
    """Tests for user login endpoint"""
    
    def test_login_success(self, client, test_user, test_user_data):
        """Test successful login"""
        response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client, test_user, test_user_data):
        """Test login with incorrect password"""
        response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent username"""
        response = client.post("/api/auth/login", data={
            "username": "nonexistent",
            "password": "somepassword"
        })
        
        assert response.status_code == 401
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post("/api/auth/login", data={})
        
        assert response.status_code == 422


@pytest.mark.auth
class TestCurrentUser:
    """Tests for current user endpoint"""
    
    def test_get_current_user(self, client, test_user, auth_headers, test_user_data):
        """Test getting current authenticated user"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["id"] == test_user.id
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        
        assert response.status_code == 401
