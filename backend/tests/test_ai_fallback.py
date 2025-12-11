import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.ai
class TestAIFallback:
    """Tests for AI fallback logic (Groq -> Hugging Face -> Ollama)"""

    @patch('app.services.ai_service.settings.GROQ_API_KEY', 'valid_groq_key')
    @patch('app.services.ai_service.settings.HUGGINGFACE_API_KEY', 'valid_hf_key')
    def test_groq_success(self, client, auth_headers):
        """Test that Groq is used when configured and works (Priority 1)"""
        from app.services.ai_service import ai_service
        
        # Patch methods on the singleton instance
        with patch.object(ai_service, '_call_groq_api', new_callable=AsyncMock) as mock_groq, \
             patch.object(ai_service, '_call_huggingface_api', new_callable=AsyncMock) as mock_hf, \
             patch.object(ai_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            
            # Re-initialize client if needed (since __init__ checks env vars)
            # Actually, ai_service is already initialized. We need to manually set clients if we want to simulate init
            # But simpler is to rely on the fact that _call_api checks self.groq_client.
            # We must set self.groq_client on the instance if it wasn't set during app startup.
            # Or we can just mock the client itself?
            # The cleanest way for tested logic is to mock _call_groq_api directly which we do.
            # BUT _call_api checks `if self.groq_client:`. So we must ensure self.groq_client is truthy.
            ai_service.groq_client = True 
            
            mock_groq.return_value = "Response from Groq"
            
            response = client.post(
                "/api/ai/translate",
                json={"text": "Medical text"},
                headers=auth_headers
            )
                    
            assert response.status_code == 200
            assert mock_groq.called
            assert not mock_hf.called
            assert not mock_ollama.called
            assert "Response from Groq" in response.get_json()["result"]

    @patch('app.services.ai_service.settings.GROQ_API_KEY', 'valid_groq_key')
    @patch('app.services.ai_service.settings.HUGGINGFACE_API_KEY', 'valid_hf_key')
    def test_fallback_to_huggingface(self, client, auth_headers):
        """Test fallback to Hugging Face when Groq fails (Priority 2)"""
        from app.services.ai_service import ai_service
        
        with patch.object(ai_service, '_call_groq_api', new_callable=AsyncMock) as mock_groq, \
             patch.object(ai_service, '_call_huggingface_api', new_callable=AsyncMock) as mock_hf, \
             patch.object(ai_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            
            ai_service.groq_client = True
            ai_service.hf_client = True
            
            # Groq fails (returns None)
            mock_groq.return_value = None
            mock_hf.return_value = "Response from Hugging Face"
            
            response = client.post(
                "/api/ai/translate",
                json={"text": "Medical text"},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert mock_groq.called
            assert mock_hf.called
            assert not mock_ollama.called
            assert "Response from Hugging Face" in response.get_json()["result"]

    @patch('app.services.ai_service.settings.GROQ_API_KEY', 'valid_groq_key')
    @patch('app.services.ai_service.settings.HUGGINGFACE_API_KEY', 'valid_hf_key')
    def test_fallback_to_ollama(self, client, auth_headers):
        """Test fallback to Ollama when Groq and HF fail (Priority 3)"""
        from app.services.ai_service import ai_service
        
        with patch.object(ai_service, '_call_groq_api', new_callable=AsyncMock) as mock_groq, \
             patch.object(ai_service, '_call_huggingface_api', new_callable=AsyncMock) as mock_hf, \
             patch.object(ai_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            
            ai_service.groq_client = True
            ai_service.hf_client = True
            
            mock_groq.return_value = None
            mock_hf.return_value = None
            mock_ollama.return_value = "Response from Ollama"
            
            response = client.post(
                "/api/ai/translate",
                json={"text": "Medical text"},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert mock_groq.called
            assert mock_hf.called
            assert mock_ollama.called
            assert "Response from Ollama" in response.get_json()["result"]

    def test_groq_not_configured(self, client, auth_headers):
        """Test proper skip of Groq if not configured"""
        from app.services.ai_service import ai_service
        
        # Use patch.object to safely unset clients for this test only
        with patch.object(ai_service, 'groq_client', None), \
             patch.object(ai_service, 'hf_client', None), \
             patch.object(ai_service, '_call_groq_api', new_callable=AsyncMock) as mock_groq, \
             patch.object(ai_service, '_call_huggingface_api', new_callable=AsyncMock) as mock_hf, \
             patch.object(ai_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            
            mock_ollama.return_value = "Response from Ollama"
            
            response = client.post(
                "/api/ai/translate",
                json={"text": "Medical text"},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert not mock_groq.called
            assert not mock_hf.called
            assert mock_ollama.called
