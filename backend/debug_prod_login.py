import requests
import json
import uuid

BASE_URL = "https://scoreflow-backend-5wu8.onrender.com/api/v1"

def test_prod_auth():
    email = f"debug_{uuid.uuid4()}@example.com"
    password = "password123"
    
    print(f"Testing with email: {email}")
    
    # 1. Register
    print("\n--- Registering ---")
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "confirm_password": password,
            "name": "Debug User"
        })
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Register Failed: {e}")
        return

    if resp.status_code != 200:
        print("Registration failed, skipping login.")
        return

    # 2. Login
    print("\n--- Logging in ---")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Login Failed: {e}")

if __name__ == "__main__":
    test_prod_auth()
