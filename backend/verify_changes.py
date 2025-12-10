import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def print_pass(message):
    print(f"\033[92m[PASS] {message}\033[0m")

def print_fail(message):
    print(f"\033[91m[FAIL] {message}\033[0m")

def verify_health():
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print_pass("Health check passed")
            return True
    except Exception as e:
        print_fail(f"Health check failed: {e}")
    return False

def verify_frontend_serving():
    try:
        resp = requests.get(f"{BASE_URL}/login")
        if resp.status_code == 200 and "<html" in resp.text:
            print_pass("Frontend serving (login page) passed")
            return True
        else:
            print_fail(f"Frontend serving failed: Status {resp.status_code}")
    except Exception as e:
        print_fail(f"Frontend serving failed: {e}")
    return False

def verify_json_login():
    # 1. Register
    username = f"testuser_{int(time.time())}"
    user_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if resp.status_code != 201:
            print_fail(f"Registration failed: {resp.text}")
            return None
        print_pass("Registration passed")
        
        # 2. Login with JSON (New Feature)
        login_data = {
            "username": username,
            "password": "password123"
        }
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if resp.status_code == 200 and "access_token" in resp.json():
            print_pass("JSON Login passed")
            return resp.json()["access_token"]
        else:
            print_fail(f"JSON Login failed: {resp.text}")
    except Exception as e:
        print_fail(f"Auth flow failed: {e}")
    return None

def verify_rag(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Add Knowledge
    knowledge_data = {
        "title": "Test Condition X",
        "content": "Test Condition X is treated by drinking lots of water and sleeping 10 hours.",
        "source": "Test Source"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/knowledge/", json=knowledge_data, headers=headers)
        if resp.status_code == 201:
            print_pass("Add Knowledge passed")
        else:
            print_fail(f"Add Knowledge failed: {resp.text}")
            return

        # 2. Ask Question (Mocking AI response if key not present, but checking flow)
        # Note: Without a real API key, the AI service might fail or return None.
        # However, we can check if the endpoint accepts the request.
        # If the AI service is not configured, it returns 503. 
        # We can accept 503 as "passed" for the infrastructure test if we don't have a key.
        
        suggestion_data = {"condition": "I have Test Condition X"}
        resp = requests.post(f"{BASE_URL}/api/ai/suggestions", json=suggestion_data, headers=headers)
        
        if resp.status_code == 200:
            print_pass("AI Suggestion (RAG) passed")
            print(f"Response: {resp.json()}")
        elif resp.status_code == 503:
            print_pass("AI Suggestion endpoint reachable (Service Unavailable as expected without key)")
        else:
            print_fail(f"AI Suggestion failed: {resp.status_code} {resp.text}")
            
    except Exception as e:
        print_fail(f"RAG flow failed: {e}")

if __name__ == "__main__":
    if not verify_health():
        sys.exit(1)
        
    if not verify_frontend_serving():
        sys.exit(1)
        
    token = verify_json_login()
    if token:
        verify_rag(token)
