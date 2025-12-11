import asyncio
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_service import ai_service
from app.config import settings

async def verify_ai():
    print("="*50)
    print("AI SERVICE VERIFICATION")
    print("="*50)
    
    print(f"Hugging Face Model: {settings.HUGGINGFACE_MODEL}")
    print(f"Groq Model:         {settings.GROQ_MODEL}")
    print(f"Ollama Model:       {settings.OLLAMA_MODEL}")
    print("-" * 30)

    # 1. Test Translation (Text Only)
    print("\n[TEST 1] Testing Text Translation (Priority: Groq -> HF -> Ollama)...")
    try:
        text = "Patient has hypertension and tachycardia."
        print(f"Input: {text}")
        result = await ai_service.translate_medical_text(text)
        if result:
            print("[OK] Success!")
            print(f"Response: {result[:100]}...")
        else:
            print("[FAIL] No response received.")
    except Exception as e:
        print(f"[ERROR] {e}")
        if "410" in str(e) or "401" in str(e) or "403" in str(e):
             print("\n[HINT] For Meta Llama models, you must:")
             print("1. Accept the license on https://huggingface.co/meta-llama")
             print("2. Ensure your API Token has 'Read' permissions")
             print("3. Wait for access approval (usually email confirmation)")

    # 2. Test Vision (if configured)
    print("\n[TEST 2] Testing Vision API (HF/Groq)...")
    is_vision_model = any(k in (settings.HUGGINGFACE_MODEL + settings.GROQ_MODEL).lower() for k in ["vision", "preview"])
    
    if not settings.HUGGINGFACE_API_KEY and not settings.GROQ_API_KEY:
        print("[SKIP] No API Keys configured.")
    elif not is_vision_model:
        print(f"[SKIP] Current model configuration unlikely to support Vision.")
    else:
        try:
            # Simple 1x1 pixel white image base64
            dummy_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGP6DwABBAEKKQV8jAAAAABJRU5ErkJggg=="
            print("Sending dummy image for analysis...")
            result = await ai_service.analyze_image(dummy_image, "What color is this image?")
            if result:
                print("[OK] Vision Analysis Connection Successful.")
                print(f"Response: {result}")
            else:
                print("[FAIL] No response from Vision API.")
        except Exception as e:
            print(f"[ERROR] Vision Test Failed: {e}")

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(verify_ai())
