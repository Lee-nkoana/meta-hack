
import sys
import os
import asyncio
from flask import Flask

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.models.medical_record import MedicalRecord
    from app.services.ai_service import ai_service
    from app.services.knowledge_base import knowledge_base
    from app.config import settings
    
    print("Verifying Application State...")
    
    # 1. Verify DB Schema Model
    if hasattr(MedicalRecord, 'image_data'):
        print("[OK] MedicalRecord model has 'image_data' column.")
    else:
        print("[FAIL] MedicalRecord model MISSING 'image_data' column.")
        sys.exit(1)
        
    # 2. Verify Config
    expected_model = "meta-llama/Llama-3.2-11B-Vision-Instruct"
    if settings.HUGGINGFACE_MODEL == expected_model:
        print(f"[OK] Config HUGGINGFACE_MODEL is '{expected_model}'.")
    else:
        print(f"[FAIL] Config HUGGINGFACE_MODEL is '{settings.HUGGINGFACE_MODEL}', expected '{expected_model}'.")
        sys.exit(1)
        
    # 3. Verify AI Service Method (Vision)
    if hasattr(ai_service, 'analyze_image'):
        print("[OK] ai_service has 'analyze_image' method.")
    else:
        print("[FAIL] ai_service MISSING 'analyze_image' method.")
        sys.exit(1)

    # 4. Verify RAG (KnowledgeBase - Lightweight JSON)
    if knowledge_base:
        print("[OK] KnowledgeBase initialized.")
        if hasattr(knowledge_base, 'file_path') and "knowledge_base.json" in knowledge_base.file_path:
             print("[OK] KnowledgeBase is using JSON storage (Lightweight Mode).")
        else:
             print("[WARN] KnowledgeBase storage type mismatch or file_path missing.")

    # 5. Check Dockerfile existence
    if os.path.exists("Dockerfile"):
        print("[OK] Dockerfile exists.")
    else:
         print("[FAIL] Dockerfile MISSING.")
         
    if os.path.exists("entrypoint.sh"):
        print("[OK] entrypoint.sh exists.")
    else:
         print("[FAIL] entrypoint.sh MISSING.")

    print("\nVerification Successful!")
    
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected Error: {e}")
    sys.exit(1)
