
import os
import json
import numpy as np
import httpx
from typing import List, Dict, Optional
from app.config import settings

class KnowledgeBase:
    """Lightweight RAG Service using JSON storage and HF API for embeddings"""
    
    def __init__(self):
        self.file_path = os.path.join(os.getcwd(), "knowledge_base.json")
        self.data: List[Dict] = []
        self._load_data()
        
    def _load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.data = json.load(f)
            except Exception:
                self.data = []
        else:
            self.data = []

    def _save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)
            
    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Hugging Face API"""
        if not settings.HUGGINGFACE_API_KEY:
            return None
            
        model_id = "sentence-transformers/all-MiniLM-L6-v2"
        api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, headers=headers, json={"inputs": text})
                if response.status_code == 200:
                    result = response.json()
                    # Handle different return formats (sometimes list of list, sometimes list)
                    if isinstance(result, list):
                        if isinstance(result[0], list):
                            return result[0] # Batched return
                        return result
                return None
        except Exception as e:
            print(f"Embedding API Error: {e}")
            return None
            
    def add_record(self, record_id: str, text: str, meta: dict = None):
        """Add record (Async wrapper needed in sync context usually, but here we might need to be sync or fire-and-forget)"""
        # For simplicity in this lightweight version, we'll try to run sync or just skip embedding if we can't await.
        # Ideally, this should be async.
        # Since the caller in medical_records.py is sync, we really should use a sync HTTP client here or run loop.
        
        # Let's use a sync storage for now, and maybe background the embedding?
        # Or just use sync requests/httpx
        import requests
        
        if not settings.HUGGINGFACE_API_KEY:
             return

        model_id = "sentence-transformers/all-MiniLM-L6-v2"
        api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
        
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=10)
            if response.status_code == 200:
                embedding = response.json()
                if isinstance(embedding, list) and isinstance(embedding[0], list):
                    embedding = embedding[0]
                
                self.data.append({
                    "id": str(record_id),
                    "text": text,
                    "meta": meta or {},
                    "embedding": embedding
                })
                self._save_data()
        except Exception as e:
            print(f"Failed to add record to KB: {e}")

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """Find relevant records using cosine similarity"""
        import requests
        if not settings.HUGGINGFACE_API_KEY:
            return []
            
        # Get query embedding
        model_id = "sentence-transformers/all-MiniLM-L6-v2"
        api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
        
        query_embedding = None
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": query_text}, timeout=10)
            if response.status_code == 200:
                query_embedding = response.json()
                if isinstance(query_embedding, list) and isinstance(query_embedding[0], list):
                    query_embedding = query_embedding[0]
        except Exception:
            return []
            
        if not query_embedding or not self.data:
            return []
            
        # Calculate Cosine Similarities
        q_vec = np.array(query_embedding)
        norm_q = np.linalg.norm(q_vec)
        
        scores = []
        for item in self.data:
            if "embedding" not in item:
                continue
            d_vec = np.array(item["embedding"])
            norm_d = np.linalg.norm(d_vec)
            
            if norm_q == 0 or norm_d == 0:
                score = 0
            else:
                score = np.dot(q_vec, d_vec) / (norm_q * norm_d)
            
            scores.append((score, item["text"]))
            
        # Sort and return top N
        scores.sort(key=lambda x: x[0], reverse=True)
        return [text for score, text in scores[:n_results]]

# Singleton
knowledge_base = KnowledgeBase()
