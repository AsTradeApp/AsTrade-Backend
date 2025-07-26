#!/usr/bin/env python3
"""
Script para probar la creación de usuarios
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Probar el registro de usuario desde frontend"""
    
    # Datos de prueba
    user_data = {
        "provider": "google",
        "email": "test@example.com",
        "cavos_user_id": "google_123456789",
        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
    }
    
    print("🧪 Testing user registration...")
    print(f"Data: {json.dumps(user_data, indent=2)}")
    
    # Llamar al endpoint de registro
    response = requests.post(
        f"{BASE_URL}/api/v1/users/register",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ User registration successful!")
        return response.json()["data"]["user_id"]
    else:
        print("❌ User registration failed!")
        return None

def test_get_user(user_id):
    """Probar obtener información del usuario"""
    if not user_id:
        print("⏭️  Skipping get user test (no user_id)")
        return
    
    print(f"\n🧪 Testing get user {user_id}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/users/{user_id}")
    
    print(f"📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get user successful!")
    else:
        print("❌ Get user failed!")

def test_health_check():
    """Probar el health check"""
    print("🧪 Testing health check...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Health check successful!")
        return True
    else:
        print("❌ Health check failed!")
        return False

if __name__ == "__main__":
    print("🚀 Starting AsTrade User Creation Tests\n")
    
    # Verificar que el servidor esté funcionando
    if not test_health_check():
        print("❌ Server is not healthy, stopping tests")
        exit(1)
    
    print("\n" + "="*50 + "\n")
    
    # Probar registro de usuario
    user_id = test_user_registration()
    
    print("\n" + "="*50 + "\n")
    
    # Probar obtener usuario
    test_get_user(user_id)
    
    print("\n�� Tests completed!") 