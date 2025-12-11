import os
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv

# Load env vars to get the key
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

async def list_models():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env")
        return

    client = AsyncGroq(api_key=api_key)
    try:
        models = await client.models.list()
        print(f"{'ID':<40} {'Owned By':<20}")
        print("-" * 60)
        for model in models.data:
            print(f"{model.id:<40} {model.owned_by:<20}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
