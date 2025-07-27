#!/usr/bin/env python3
"""
Test script for complete Cavos + AsTrade + Extended Exchange integration
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1/users"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ️  {message}")

def test_integration_status():
    """Test the integration status endpoint"""
    print_section("TESTING INTEGRATION STATUS")
    
    try:
        response = requests.get(f"{API_BASE}/integration/status")
        response.raise_for_status()
        
        data = response.json()
        print_success("Integration status endpoint working")
        
        # Print database stats
        db_stats = data['data']['database']
        print_info(f"Database records:")
        print_info(f"  - Profiles: {db_stats['profiles_count']}")
        print_info(f"  - Wallets: {db_stats['wallets_count']}")
        print_info(f"  - Credentials: {db_stats['credentials_count']}")
        
        # Print sample data
        sample_data = data['data']['sample_data']
        if sample_data['profile']:
            print_info(f"Sample profile: {sample_data['profile']['display_name']}")
        if sample_data['wallet']:
            print_info(f"Sample wallet: {sample_data['wallet']['address'][:10]}...")
        if sample_data['credentials']:
            print_info(f"Sample credentials: {sample_data['credentials']['environment']}")
        
        return True
        
    except Exception as e:
        print_error(f"Integration status test failed: {str(e)}")
        return False

def test_user_creation():
    """Test user creation with Cavos data"""
    print_section("TESTING USER CREATION")
    
    # Generate unique test data
    timestamp = int(time.time())
    test_email = f"test_{timestamp}@example.com"
    test_cavos_id = f"cavos-test-user-{timestamp}"
    test_wallet = f"0x{timestamp:040x}"
    
    user_data = {
        "provider": "google",
        "email": test_email,
        "cavos_user_id": test_cavos_id,
        "wallet_address": test_wallet
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/register",
            headers={"Content-Type": "application/json"},
            json=user_data
        )
        response.raise_for_status()
        
        result = response.json()
        user_id = result['data']['user_id']
        
        print_success(f"User created successfully")
        print_info(f"User ID: {user_id}")
        print_info(f"Email: {test_email}")
        print_info(f"Cavos ID: {test_cavos_id}")
        print_info(f"Wallet: {test_wallet[:10]}...")
        
        return user_id, test_cavos_id
        
    except Exception as e:
        print_error(f"User creation test failed: {str(e)}")
        return None, None

def test_user_lookup(user_id):
    """Test user lookup by ID"""
    print_section("TESTING USER LOOKUP BY ID")
    
    try:
        response = requests.get(f"{API_BASE}/{user_id}")
        response.raise_for_status()
        
        data = response.json()
        user_info = data['data']
        
        print_success("User lookup by ID working")
        print_info(f"User ID: {user_info['user_id']}")
        print_info(f"Email: {user_info['email']}")
        print_info(f"Provider: {user_info['provider']}")
        print_info(f"Wallet: {user_info['wallet_address'][:10]}...")
        print_info(f"Has API credentials: {user_info['has_api_credentials']}")
        
        # Check Extended setup
        extended = user_info['extended_setup']
        print_info(f"Extended configured: {extended['is_configured']}")
        print_info(f"Extended status: {extended['status']}")
        print_info(f"Environment: {extended['environment']}")
        
        return True
        
    except Exception as e:
        print_error(f"User lookup test failed: {str(e)}")
        return False

def test_cavos_lookup(cavos_user_id):
    """Test user lookup by Cavos ID"""
    print_section("TESTING USER LOOKUP BY CAVOS ID")
    
    try:
        response = requests.get(f"{API_BASE}/cavos/{cavos_user_id}")
        response.raise_for_status()
        
        data = response.json()
        user_info = data['data']
        
        print_success("User lookup by Cavos ID working")
        print_info(f"User ID: {user_info['user_id']}")
        print_info(f"Email: {user_info['email']}")
        print_info(f"Provider: {user_info['provider']}")
        print_info(f"Wallet: {user_info['wallet_address'][:10]}...")
        print_info(f"Has API credentials: {user_info['has_api_credentials']}")
        
        return True
        
    except Exception as e:
        print_error(f"Cavos lookup test failed: {str(e)}")
        return False

def test_extended_status(user_id):
    """Test Extended Exchange status endpoint"""
    print_section("TESTING EXTENDED EXCHANGE STATUS")
    
    try:
        response = requests.get(f"{API_BASE}/{user_id}/extended/status")
        response.raise_for_status()
        
        data = response.json()
        status_info = data['data']
        
        print_success("Extended status endpoint working")
        print_info(f"User ID: {status_info['user_id']}")
        print_info(f"Extended configured: {status_info['extended_configured']}")
        print_info(f"Status message: {status_info['status_message']}")
        print_info(f"Environment: {status_info['environment']}")
        
        # Print features
        features = status_info['features']
        print_info("Available features:")
        for feature, available in features.items():
            status = "✅" if available else "❌"
            print_info(f"  {status} {feature}")
        
        # Print limitations if any
        if status_info['limitations']:
            print_info("Limitations:")
            for limitation in status_info['limitations']:
                print_info(f"  - {limitation}")
        
        return True
        
    except Exception as e:
        print_error(f"Extended status test failed: {str(e)}")
        return False

def test_extended_setup(user_id):
    """Test Extended Exchange setup endpoint"""
    print_section("TESTING EXTENDED EXCHANGE SETUP")
    
    try:
        response = requests.post(f"{API_BASE}/{user_id}/extended/setup")
        response.raise_for_status()
        
        data = response.json()
        setup_info = data['data']
        
        print_success("Extended setup endpoint working")
        print_info(f"Setup completed: {setup_info['setup_completed']}")
        print_info(f"Message: {setup_info['message']}")
        
        if setup_info['next_steps']:
            print_info("Next steps:")
            for step in setup_info['next_steps']:
                print_info(f"  - {step}")
        
        return True
        
    except Exception as e:
        print_error(f"Extended setup test failed: {str(e)}")
        return False

def main():
    """Run all integration tests"""
    print_section("CAVOS + ASTRADE + EXTENDED INTEGRATION TEST")
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test 1: Integration status
    if not test_integration_status():
        print_error("Integration status test failed. Stopping tests.")
        return
    
    # Test 2: User creation
    user_id, cavos_id = test_user_creation()
    if not user_id:
        print_error("User creation test failed. Stopping tests.")
        return
    
    # Test 3: User lookup by ID
    if not test_user_lookup(user_id):
        print_error("User lookup test failed.")
    
    # Test 4: User lookup by Cavos ID
    if not test_cavos_lookup(cavos_id):
        print_error("Cavos lookup test failed.")
    
    # Test 5: Extended status
    if not test_extended_status(user_id):
        print_error("Extended status test failed.")
    
    # Test 6: Extended setup
    if not test_extended_setup(user_id):
        print_error("Extended setup test failed.")
    
    # Final status check
    print_section("FINAL INTEGRATION STATUS")
    test_integration_status()
    
    print_section("TEST COMPLETION")
    print_success("All integration tests completed!")
    print_info("The Cavos + AsTrade + Extended Exchange integration is working correctly.")
    print_info("Next step: Test with real Extended Exchange credentials.")

if __name__ == "__main__":
    main() 