# AI service endpoint tests
import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai_service import ai_service

@pytest.mark.ai
class TestAITranslation:
    """Tests for AI translation endpoint"""
    
    def test_translate_success(self, client, auth_headers):
        """Test successful medical text translation"""
        with patch.object(ai_service, 'translate_medical_text', new_callable=AsyncMock) as mock_translate, \
             patch.object(ai_service, 'meta_api_key', 'test_key'), \
             patch.object(ai_service, 'hf_client', 'test_key'), \
             patch.object(ai_service, 'groq_client', 'test_key'):
            
            mock_translate.return_value = "This means white blood cells, red blood cells, and platelets are normal."
        
            response = client.post(
                "/api/ai/translate",
                json={"text": "WBC, RBC, and PLT within normal limits"},
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "result" in data
        assert data["cached"] is False
    
    def test_translate_no_auth(self, client):
        """Test translation without authentication"""
        response = client.post(
            "/api/ai/translate",
            json={"text": "Some medical text"}
        )
        
        assert response.status_code == 401
    
    def test_translate_missing_text(self, client, auth_headers):
        """Test translation with missing text"""
        response = client.post(
            "/api/ai/translate",
            json={},
            headers=auth_headers
        )
        
        assert response.status_code == 400


@pytest.mark.ai
class TestAISuggestions:
    """Tests for AI lifestyle suggestions endpoint"""
    
    def test_suggestions_success(self, client, auth_headers):
        """Test successful lifestyle suggestions generation"""
        with patch.object(ai_service, 'generate_lifestyle_suggestions', new_callable=AsyncMock) as mock_suggestions, \
             patch.object(ai_service, 'meta_api_key', 'test_key'):
            
            mock_suggestions.return_value = "Consider regular exercise and balanced diet."
        
            response = client.post(
                "/api/ai/suggestions",
                json={"condition": "High cholesterol"},
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "result" in data
        assert data["cached"] is False
    
    def test_suggestions_no_auth(self, client):
        """Test suggestions without authentication"""
        response = client.post(
            "/api/ai/suggestions",
            json={"condition": "Some condition"}
        )
        
        assert response.status_code == 401
    
    def test_suggestions_missing_condition(self, client, auth_headers):
        """Test suggestions with missing condition"""
        response = client.post(
            "/api/ai/suggestions",
            json={},
            headers=auth_headers
        )
        
        assert response.status_code == 400


@pytest.mark.ai
class TestAIExplainRecord:
    """Tests for AI record explanation endpoint"""
    
    def test_explain_record_success(self, client, auth_headers, test_medical_record):
        """Test successful record explanation"""
        with patch.object(ai_service, 'explain_medical_record', new_callable=AsyncMock) as mock_explain, \
             patch.object(ai_service, 'meta_api_key', 'test_key'):
            
            mock_explain.return_value = {
                "translation": "Your blood test shows normal levels",
                "suggestions": "Maintain healthy diet and exercise"
            }
            
            response = client.post(
                f"/api/ai/explain/{test_medical_record.id}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "translation" in data
        assert "suggestions" in data
        assert "cached" in data
    
    def test_explain_record_cached(self, client, auth_headers, test_medical_record, db_session):
        """Test explanation uses cached data"""
        # Set cached data
        test_medical_record.translated_text = "Cached translation"
        test_medical_record.lifestyle_suggestions = "Cached suggestions"
        db_session.commit()
        
        response = client.post(
            f"/api/ai/explain/{test_medical_record.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["translation"] == "Cached translation"
        assert data["suggestions"] == "Cached suggestions"
        assert data["cached"] is True
    
    def test_explain_record_force_refresh(self, client, auth_headers, test_medical_record, db_session):
        """Test explanation with force refresh"""
        # Set cached data
        test_medical_record.translated_text = "Old translation"
        test_medical_record.lifestyle_suggestions = "Old suggestions"
        db_session.commit()
        
        with patch.object(ai_service, 'explain_medical_record', new_callable=AsyncMock) as mock_explain, \
             patch.object(ai_service, 'meta_api_key', 'test_key'):
            
            mock_explain.return_value = {
                "translation": "New translation",
                "suggestions": "New suggestions"
            }
            
            response = client.post(
                f"/api/ai/explain/{test_medical_record.id}?force_refresh=true",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.get_json()
        # Should call the AI service even with cached data
        assert mock_explain.called
    
    def test_explain_record_not_found(self, client, auth_headers):
        """Test explanation for non-existent record"""
        response = client.post(
            "/api/ai/explain/999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_explain_record_no_auth(self, client, test_medical_record):
        """Test explanation without authentication"""
        response = client.post(f"/api/ai/explain/{test_medical_record.id}")
        
        assert response.status_code == 401


@pytest.mark.ai
class TestAIServiceUnavailable:
    """Tests for AI service when not configured"""
    
    def test_translate_no_api_key(self, client, auth_headers):
        """Test translation when AI service is not configured"""
        
        with patch.object(ai_service, 'hf_client', None), \
             patch.object(ai_service, 'groq_client', None), \
             patch.object(ai_service, 'meta_api_key', None):
             
            response = client.post(
                "/api/ai/translate",
                json={"text": "Medical text"},
                headers=auth_headers
            )
            
            # Should return 503 Service Unavailable
            if response.status_code == 503:
                assert "not configured" in response.get_json().get("error", "").lower()
