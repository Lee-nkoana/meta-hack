# Meta AI service for medical text translation and lifestyle suggestions
import httpx
from typing import Optional
from app.config import settings


class AIService:
    """Service for Meta AI integration (using Together AI API for Llama models)"""
    
    def __init__(self):
        self.api_key = settings.META_AI_API_KEY
        self.base_url = settings.META_AI_BASE_URL
        self.model = settings.META_AI_MODEL
        self.temperature = settings.META_AI_TEMPERATURE
        self.max_tokens = settings.META_AI_MAX_TOKENS
    
    @property
    def is_configured(self) -> bool:
        """Check if any AI service is configured (Ollama is always available as fallback)"""
        return True
    
    async def _call_ollama_api(self, prompt: str, system_message: str) -> Optional[str]:
        """Call local Ollama API"""
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("message", {}).get("content")
                elif response.status_code == 404:
                    return f"System: The Ollama model '{settings.OLLAMA_MODEL}' is not found. It might still be downloading. Please wait a few minutes."
        except Exception as e:
            print(f"Ollama API Error: {str(e)}")
            return None
        return None

    async def _call_huggingface_api(self, prompt: str, system_message: str) -> Optional[str]:
        """Call the Hugging Face Inference API"""
        if not settings.HUGGINGFACE_API_KEY:
            return None
            
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Use a specific Llama 3 model URL
        model_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
        
        payload = {
            "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "parameters": {
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
                "return_full_text": False
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    model_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                # Hugging Face usually returns a list of result dicts
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", "").strip()
                return None
        except Exception as e:
            print(f"Hugging Face API Error: {str(e)}")
            return None

    async def _call_api(self, prompt: str, system_message: str) -> Optional[str]:
        """Call the AI API with prioritization: Ollama -> HuggingFace -> Together"""
        
        # Priority 1: Ollama (Local)
        ollama_response = await self._call_ollama_api(prompt, system_message)
        if ollama_response:
            return ollama_response
            
        # Priority 2: Hugging Face
        if settings.HUGGINGFACE_API_KEY:
            hf_response = await self._call_huggingface_api(prompt, system_message)
            if hf_response:
                return hf_response
            
        # Priority 3: Together AI (Meta AI)
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI API Error: {str(e)}")
            return None
    
    async def translate_medical_text(self, medical_text: str) -> Optional[str]:
        """Translate medical jargon into layman's terms"""
        system_message = """You are a helpful medical translator. Your job is to translate medical jargon 
        and technical terms into simple, easy-to-understand language that patients can comprehend. 
        Be clear, accurate, and empathetic. Do not provide medical advice."""
        
        prompt = f"""Please translate the following medical text into simple, easy-to-understand language 
        that a patient without medical training can understand. Explain any medical terms, abbreviations, 
        and concepts clearly:

{medical_text}

Provide a clear, patient-friendly explanation:"""
        
        return await self._call_api(prompt, system_message)
    
    async def generate_lifestyle_suggestions(self, medical_condition: str) -> Optional[str]:
        """Generate lifestyle suggestions for a medical condition"""
        system_message = """You are a helpful wellness advisor. Based on medical conditions described, 
        you provide general lifestyle tips and suggestions that may help patients manage their condition. 
        IMPORTANT: You do NOT provide medical advice, diagnoses, or treatment recommendations. 
        You only suggest general lifestyle improvements like diet, exercise, sleep, stress management, etc. 
        Always remind users to consult their healthcare provider."""
        
        prompt = f"""Based on the following medical information, suggest some general lifestyle tips 
        that might help the patient. Focus on diet, exercise, sleep, stress management, and daily habits. 
        Remember: DO NOT give medical advice or suggest treatments. Only provide general wellness suggestions.

Medical Information:
{medical_condition}

Please provide helpful lifestyle suggestions:"""
        
        return await self._call_api(prompt, system_message)
    
    async def chat_with_patient(self, message: str, context: Optional[str] = None) -> Optional[str]:
        """Chat with patient using their medical context"""
        system_message = """You are a helpful and empathetic medical assistant. You are chatting with a patient 
        who uses the "Medical Records Bridge" app. 
        
        Your Role:
        1. Answer the patient's questions based on their medical records context if provided.
        2. Be supportive, clear, and reassuring.
        3. Explain medical concepts in simple terms.
        
        CRITICAL RULES:
        1. DO NOT provide medical advice, diagnosis, or prescribe treatments.
        2. Always encourage the patient to consult their real healthcare provider for symptoms.
        3. If you don't know the answer from the context, admit it.
        """
        
        if context:
            prompt = f"""Context from my medical records:
{context}

My Question: {message}"""
        else:
            prompt = message
            
        return await self._call_api(prompt, system_message)

    async def explain_medical_record(self, record_text: str, record_type: str = "doctor_note") -> dict:
        """Get both translation and suggestions for a medical record"""
        translation = await self.translate_medical_text(record_text)
        suggestions = await self.generate_lifestyle_suggestions(record_text)
        
        return {
            "translation": translation,
            "suggestions": suggestions
        }


# Create singleton instance
ai_service = AIService()
