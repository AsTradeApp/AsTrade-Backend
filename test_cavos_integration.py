#!/usr/bin/env python3
"""
Script para probar la integración con Cavos
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def test_cavos_user_creation():
    """Probar la creación de usuario con datos de Cavos"""
    
    # Datos simulados de Cavos
    cavos_user_data = {
        "provider": "google",
        "email": "cavos_test@example.com",
        "cavos_user_id": "cavos-test-user-123",
        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
    }
    
    print("🧪 Testing Cavos user creation...")
    print(f"Data: {json.dumps(cavos_user_data, indent=2)}")
    
    # Llamar al endpoint de registro
    response = requests.post(
        f"{BASE_URL}/api/v1/users/register",
        json=cavos_user_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Cavos user creation successful!")
        user_data = response.json()["data"]
        return user_data["user_id"]
    else:
        print("❌ Cavos user creation failed!")
        return None

def test_get_user_by_cavos_id(cavos_user_id):
    """Probar obtener usuario por Cavos ID"""
    if not cavos_user_id:
        print("⏭️  Skipping get user by Cavos ID test (no cavos_user_id)")
        return
    
    print(f"\n🧪 Testing get user by Cavos ID: {cavos_user_id}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/users/cavos/{cavos_user_id}")
    
    print(f"📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get user by Cavos ID successful!")
    else:
        print("❌ Get user by Cavos ID failed!")

def test_duplicate_registration():
    """Probar registro duplicado del mismo usuario"""
    print("\n🧪 Testing duplicate registration...")
    
    # Usar los mismos datos
    cavos_user_data = {
        "provider": "google",
        "email": "cavos_test@example.com",
        "cavos_user_id": "cavos-test-user-123",
        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/users/register",
        json=cavos_user_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Duplicate registration handled correctly!")
    else:
        print("❌ Duplicate registration failed!")

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
    print("🚀 Starting AsTrade Cavos Integration Tests\n")
    
    # Verificar que el servidor esté funcionando
    if not test_health_check():
        print("❌ Server is not healthy, stopping tests")
        exit(1)
    
    print("\n" + "="*50 + "\n")
    
    # Probar creación de usuario con Cavos
    user_id = test_cavos_user_creation()
    
    print("\n" + "="*50 + "\n")
    
    # Probar obtener usuario por Cavos ID
    test_get_user_by_cavos_id("cavos-test-user-123")
    
    print("\n" + "="*50 + "\n")
    
    # Probar registro duplicado
    test_duplicate_registration()
    
    print("\n�� Tests completed!") 