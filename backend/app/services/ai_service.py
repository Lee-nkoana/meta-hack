# Meta AI service for medical text translation and lifestyle suggestions
import httpx
from typing import Optional
from huggingface_hub import AsyncInferenceClient
from groq import AsyncGroq
from app.config import settings


class AIService:
    """Service for Meta AI integration (using Hugging Face and Groq)"""
    
    def __init__(self):
        # Configuration
        self.max_tokens = settings.META_AI_MAX_TOKENS
        self.temperature = settings.META_AI_TEMPERATURE
        
        # Initialize Hugging Face Client
        self.hf_client = None
        if settings.HUGGINGFACE_API_KEY:
             self.hf_client = AsyncInferenceClient(
                 model=settings.HUGGINGFACE_MODEL,
                 token=settings.HUGGINGFACE_API_KEY
             )

        # Initialize Groq Client
        self.groq_client = None
        if settings.GROQ_API_KEY:
            self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.groq_model = settings.GROQ_MODEL

        # Legacy Together AI fallback config
        self.meta_api_key = settings.META_AI_API_KEY
    
    @property
    def is_configured(self) -> bool:
        """Check if any AI service is configured"""
        return bool(self.hf_client) or bool(self.groq_client) or bool(self.meta_api_key) or bool(settings.OLLAMA_BASE_URL)
    
    async def _call_ollama_api(self, prompt: str, system_message: str) -> Optional[str]:
        """Call local Ollama API (Fallback)"""
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
        except Exception as e:
            print(f"Ollama API Error: {str(e)}")
            return None
        return None

    async def _call_huggingface_api(self, prompt: str, system_message: str, image_b64: Optional[str] = None) -> Optional[str]:
        """Call Hugging Face using AsyncInferenceClient"""
        if not self.hf_client:
            return None
            
        messages = [{"role": "system", "content": system_message}]
        
        if image_b64:
            image_data_url = f"data:image/jpeg;base64,{image_b64}"
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": prompt}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})
            
        try:
            response = await self.hf_client.chat_completion(
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            return None
        except Exception as e:
            print(f"Hugging Face Inference Error: {e}")
            return None

    async def _call_groq_api(self, prompt: str, system_message: str, image_b64: Optional[str] = None) -> Optional[str]:
        """Call Groq API"""
        if not self.groq_client:
            return None
            
        messages = [{"role": "system", "content": system_message}]
        
        if image_b64:
            # Groq implementation for Llama 3.2 Vision
            image_data_url = f"data:image/jpeg;base64,{image_b64}"
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": prompt}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})
            
        try:
            response = await self.groq_client.chat.completions.create(
                messages=messages,
                model=self.groq_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            return None

    async def _call_api(self, prompt: str, system_message: str, image_b64: Optional[str] = None) -> Optional[str]:
        """Call the AI API with prioritization: Groq -> HuggingFace -> Ollama"""
        
        # Priority 1: Groq (Fastest, Smartest 70B model)
        if self.groq_client:
            groq_response = await self._call_groq_api(prompt, system_message, image_b64)
            if groq_response:
                return groq_response
            print("Groq API failed, trying Hugging Face...")

        # Priority 2: Hugging Face (Fallback)
        if self.hf_client:
            hf_response = await self._call_huggingface_api(prompt, system_message, image_b64)
            if hf_response:
                return hf_response
            print("Hugging Face API failed, trying Ollama...")
            
        # Priority 3: Ollama (Local)
        if not image_b64:
             ollama_response = await self._call_ollama_api(prompt, system_message)
             if ollama_response:
                 return ollama_response
            
        return None
    
    async def translate_medical_text(self, medical_text: str) -> Optional[str]:
        """Translate medical jargon into layman's terms"""
        system_message = "You are a helpful medical translator. Translate medical jargon into simple, patient-friendly language. Do not provide medical advice."
        prompt = f"Translate and explain this medically:\n\n{medical_text}"
        return await self._call_api(prompt, system_message)
    
    async def generate_lifestyle_suggestions(self, medical_condition: str) -> Optional[str]:
        """Generate lifestyle suggestions"""
        system_message = "You are a wellness advisor. Provide general lifestyle tips (diet, sleep, etc) for the condition. DO NOT give medical advice."
        prompt = f"Suggest lifestyle tips for:\n\n{medical_condition}"
        return await self._call_api(prompt, system_message)
    
    async def chat_with_patient(self, message: str, context: Optional[str] = None) -> Optional[str]:
        """Chat with patient using context"""
        system_message = "You are a helpful and empathetic medical assistant. Answer based on context. Do not diagnose."
        
        # RAG Retrieval
        if not context:
            try:
                from app.services.knowledge_base import knowledge_base
                docs = knowledge_base.query(message)
                if docs: context = "\n---\n".join(docs)
            except: pass
            
        prompt = f"Context:\n{context}\n\nQuestion: {message}" if context else message
        return await self._call_api(prompt, system_message)

    async def analyze_image(self, image_b64: str, prompt: str = "Describe this medical document") -> Optional[str]:
        """Analyze a medical image using Hugging Face Vision capability"""
        # We reuse the unified API helper which supports images
        system_message = "You are an AI medical imaging assistant. Describe the image in detail. Do not diagnose."
        return await self._call_api(prompt, system_message, image_b64=image_b64)

    async def explain_medical_record(self, record_text: str, record_type: str = "doctor_note") -> dict:
        """Get both translation and suggestions"""
        return {
            "translation": await self.translate_medical_text(record_text),
            "suggestions": await self.generate_lifestyle_suggestions(record_text)
        }


# Create singleton instance
ai_service = AIService()
