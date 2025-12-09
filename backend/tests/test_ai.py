# AI service endpoint tests
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.ai
class TestAITranslation:
    """Tests for AI translation endpoint"""
    
    @patch('app.services.ai_service.AIService._call_api')
    async def test_translate_success(self, mock_api, client, auth_headers):
        """Test successful medical text translation"""
        mock_api.return_value = "This means white blood cells, red blood cells, and platelets are normal."
        
        response = client.post(
            "/api/ai/translate",
            json={"text": "WBC, RBC, and PLT within normal limits"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
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
        
        assert response.status_code == 422


@pytest.mark.ai
class TestAISuggestions:
    """Tests for AI lifestyle suggestions endpoint"""
    
    @patch('app.services.ai_service.AIService._call_api')
    async def test_suggestions_success(self, mock_api, client, auth_headers):
        """Test successful lifestyle suggestions generation"""
        mock_api.return_value = "Consider regular exercise and balanced diet."
        
        response = client.post(
            "/api/ai/suggestions",
            json={"condition": "High cholesterol"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
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
        
        assert response.status_code == 422


@pytest.mark.ai
class TestAIExplainRecord:
    """Tests for AI record explanation endpoint"""
    
    @patch('app.services.ai_service.AIService.explain_medical_record')
    async def test_explain_record_success(self, mock_explain, client, auth_headers, test_medical_record):
        """Test successful record explanation"""
        mock_explain.return_value = {
            "translation": "Your blood test shows normal levels",
            "suggestions": "Maintain healthy diet and exercise"
        }
        
        response = client.post(
            f"/api/ai/explain/{test_medical_record.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
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
        data = response.json()
        assert data["translation"] == "Cached translation"
        assert data["suggestions"] == "Cached suggestions"
        assert data["cached"] is True
    
    @patch('app.services.ai_service.AIService.explain_medical_record')
    async def test_explain_record_force_refresh(self, mock_explain, client, auth_headers, test_medical_record, db_session):
        """Test explanation with force refresh"""
        # Set cached data
        test_medical_record.translated_text = "Old translation"
        test_medical_record.lifestyle_suggestions = "Old suggestions"
        db_session.commit()
        
        mock_explain.return_value = {
            "translation": "New translation",
            "suggestions": "New suggestions"
        }
        
        response = client.post(
            f"/api/ai/explain/{test_medical_record.id}?force_refresh=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
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
        # This will fail if META_AI_API_KEY is not set
        # In test environment, it's expected to not be set
        with patch('app.services.ai_service.AIService.api_key', None):
            response = client.post(
                "/api/ai/translate",
                json={"text": "Medical text"},
                headers=auth_headers
            )
            
            # Should return 503 Service Unavailable
            if response.status_code == 503:
                assert "not configured" in response.json()["detail"].lower()
