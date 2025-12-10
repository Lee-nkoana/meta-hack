# Medical records endpoint tests
import pytest


@pytest.mark.records
class TestCreateMedicalRecord:
    """Tests for creating medical records"""
    
    def test_create_record_success(self, client, auth_headers, test_medical_record_data):
        """Test successful medical record creation"""
        response = client.post(
            "/api/records",
            json=test_medical_record_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == test_medical_record_data["title"]
        assert data["original_text"] == test_medical_record_data["original_text"]
        assert data["record_type"] == test_medical_record_data["record_type"]
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert data["translated_text"] is None
        assert data["lifestyle_suggestions"] is None
    
    def test_create_record_no_auth(self, client, test_medical_record_data):
        """Test creating record without authentication"""
        response = client.post("/api/records", json=test_medical_record_data)
        
        assert response.status_code == 401
    
    def test_create_record_missing_title(self, client, auth_headers):
        """Test creating record without title"""
        response = client.post(
            "/api/records",
            json={"original_text": "Some text", "record_type": "doctor_note"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_create_record_missing_text(self, client, auth_headers):
        """Test creating record without original text"""
        response = client.post(
            "/api/records",
            json={"title": "Test", "record_type": "doctor_note"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_create_record_default_type(self, client, auth_headers):
        """Test creating record with default record type"""
        response = client.post(
            "/api/records",
            json={"title": "Test", "original_text": "Some text"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.get_json()["record_type"] == "doctor_note"


@pytest.mark.records
class TestListMedicalRecords:
    """Tests for listing medical records"""
    
    def test_list_records_empty(self, client, auth_headers):
        """Test listing records when user has none"""
        response = client.get("/api/records", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.get_json() == []
    
    def test_list_records_with_data(self, client, auth_headers, multiple_medical_records):
        """Test listing records when user has multiple"""
        response = client.get("/api/records", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 5
        assert all("id" in record for record in data)
        assert all("title" in record for record in data)
        assert all("has_translation" in record for record in data)
        assert all("has_suggestions" in record for record in data)
    
    def test_list_records_no_auth(self, client):
        """Test listing records without authentication"""
        response = client.get("/api/records")
        
        assert response.status_code == 401
    
    def test_list_records_pagination(self, client, auth_headers, multiple_medical_records):
        """Test listing records with pagination"""
        response = client.get("/api/records?skip=2&limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2


@pytest.mark.records
class TestGetMedicalRecord:
    """Tests for getting a specific medical record"""
    
    def test_get_record_success(self, client, auth_headers, test_medical_record):
        """Test successfully getting a medical record"""
        response = client.get(
            f"/api/records/{test_medical_record.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == test_medical_record.id
        assert data["title"] == test_medical_record.title
        assert data["original_text"] == test_medical_record.original_text
    
    def test_get_record_not_found(self, client, auth_headers):
        """Test getting non-existent record"""
        response = client.get("/api/records/999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_record_no_auth(self, client, test_medical_record):
        """Test getting record without authentication"""
        response = client.get(f"/api/records/{test_medical_record.id}")
        
        assert response.status_code == 401


@pytest.mark.records
class TestUpdateMedicalRecord:
    """Tests for updating medical records"""
    
    def test_update_record_title(self, client, auth_headers, test_medical_record):
        """Test updating record title"""
        response = client.put(
            f"/api/records/{test_medical_record.id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Updated Title"
        assert data["original_text"] == test_medical_record.original_text
    
    def test_update_record_text_clears_cache(self, client, auth_headers, test_medical_record, db_session):
        """Test that updating text clears AI cache"""
        # Add cached data
        test_medical_record.translated_text = "Cached translation"
        test_medical_record.lifestyle_suggestions = "Cached suggestions"
        db_session.commit()
        
        response = client.put(
            f"/api/records/{test_medical_record.id}",
            json={"original_text": "New text"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["original_text"] == "New text"
        assert data["translated_text"] is None
        assert data["lifestyle_suggestions"] is None
    
    def test_update_record_not_found(self, client, auth_headers):
        """Test updating non-existent record"""
        response = client.put(
            "/api/records/999",
            json={"title": "Updated"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_update_record_no_auth(self, client, test_medical_record):
        """Test updating record without authentication"""
        response = client.put(
            f"/api/records/{test_medical_record.id}",
            json={"title": "Updated"}
        )
        
        assert response.status_code == 401


@pytest.mark.records
class TestDeleteMedicalRecord:
    """Tests for deleting medical records"""
    
    def test_delete_record_success(self, client, auth_headers, test_medical_record):
        """Test successfully deleting a record"""
        response = client.delete(
            f"/api/records/{test_medical_record.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(
            f"/api/records/{test_medical_record.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_record_not_found(self, client, auth_headers):
        """Test deleting non-existent record"""
        response = client.delete("/api/records/999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_record_no_auth(self, client, test_medical_record):
        """Test deleting record without authentication"""
        response = client.delete(f"/api/records/{test_medical_record.id}")
        
        assert response.status_code == 401
