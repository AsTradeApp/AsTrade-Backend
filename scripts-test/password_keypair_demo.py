#!/usr/bin/env python3
"""
Demonstration of password-based keypair generation for Starknet

This script shows how to generate deterministic keypairs from passwords
using different key derivation functions (KDFs).
"""

import base64
from app.services.extended.stark_crypto import StarkCrypto


def demo_password_keypair_generation():
    """Demonstrate password-based keypair generation"""
    
    print("🔐 Password-Based Keypair Generation Demo")
    print("=" * 50)
    
    # Example password (in real usage, this would be user input)
    password = "MySecurePassword123!"
    
    # Method 1: Generate keypair with random salt
    print("\n1️⃣ Generate keypair with random salt:")
    key_pair1, salt1 = StarkCrypto.generate_key_pair_from_password(
        password=password,
        method="pbkdf2"
    )
    
    print(f"Private Key: {key_pair1.private_key}")
    print(f"Public Key:  {key_pair1.public_key}")
    print(f"Salt (base64): {base64.b64encode(salt1).decode()}")
    
    # Method 2: Regenerate the same keypair using the salt
    print("\n2️⃣ Regenerate the SAME keypair using stored salt:")
    key_pair2 = StarkCrypto.regenerate_key_pair_from_password(
        password=password,
        salt=salt1,
        method="pbkdf2"
    )
    
    print(f"Private Key: {key_pair2.private_key}")
    print(f"Public Key:  {key_pair2.public_key}")
    print(f"Keys match:  {key_pair1.private_key == key_pair2.private_key}")
    
    # Method 3: Different methods produce different keys
    print("\n3️⃣ Different KDF methods produce different keys:")
    
    # Using PBKDF2
    key_pair_pbkdf2, salt_pbkdf2 = StarkCrypto.generate_key_pair_from_password(
        password=password,
        salt=b"fixed_salt_for_demo" + b"\x00" * 16,  # 32 bytes total
        method="pbkdf2"
    )
    
    # Using scrypt
    key_pair_scrypt, salt_scrypt = StarkCrypto.generate_key_pair_from_password(
        password=password,
        salt=b"fixed_salt_for_demo" + b"\x00" * 16,  # Same salt, different method
        method="scrypt"
    )
    
    print(f"PBKDF2 Private:  {key_pair_pbkdf2.private_key[:16]}...")
    print(f"Scrypt Private:  {key_pair_scrypt.private_key[:16]}...")
    print(f"Different keys:  {key_pair_pbkdf2.private_key != key_pair_scrypt.private_key}")
    
    # Method 4: Different passwords produce different keys
    print("\n4️⃣ Different passwords produce different keys:")
    
    key_pair_a, _ = StarkCrypto.generate_key_pair_from_password(
        password="password_a",
        salt=b"same_salt_different_password" + b"\x00" * 7,
        method="pbkdf2"
    )
    
    key_pair_b, _ = StarkCrypto.generate_key_pair_from_password(
        password="password_b", 
        salt=b"same_salt_different_password" + b"\x00" * 7,  # Same salt
        method="pbkdf2"
    )
    
    print(f"Password A Key:  {key_pair_a.private_key[:16]}...")
    print(f"Password B Key:  {key_pair_b.private_key[:16]}...")
    print(f"Different keys:  {key_pair_a.private_key != key_pair_b.private_key}")


def demo_use_cases():
    """Show practical use cases for password-based keypairs"""
    
    print("\n\n🎯 Practical Use Cases")
    print("=" * 30)
    
    print("\n✅ Use Case 1: User Account Recovery")
    print("   - User enters password + stored salt")
    print("   - System regenerates exact same keypair")
    print("   - No need to store private keys in database")
    
    print("\n✅ Use Case 2: Deterministic Wallets")
    print("   - Same password always generates same keys")
    print("   - User can recreate wallet on any device")
    print("   - Backup = password + salt")
    
    print("\n✅ Use Case 3: Password-Protected Keys")
    print("   - Even if database is compromised, keys are safe")
    print("   - Attacker needs both salt AND password")
    print("   - Can add additional factors (2FA, etc.)")
    
    print("\n⚠️  Security Considerations:")
    print("   - Use strong passwords (entropy matters)")
    print("   - Store salts securely but separately from passwords")
    print("   - Consider key stretching (high iteration counts)")
    print("   - scrypt is more memory-hard than PBKDF2")


def demo_integration_example():
    """Show how to integrate with existing system"""
    
    print("\n\n🔧 Integration Example")
    print("=" * 25)
    
    # Simulate user registration with password
    user_password = "UserChosenPassword456"
    
    print(f"📝 User Registration Process:")
    print(f"   1. User provides password: '{user_password}'")
    
    # Generate credentials
    credentials, salt = StarkCrypto.generate_key_pair_from_password(
        password=user_password,
        method="scrypt"  # More secure for passwords
    )
    
    print(f"   2. System generates keypair + salt")
    print(f"   3. Store salt in database (not the private key!)")
    print(f"   4. Salt: {base64.b64encode(salt).decode()[:32]}...")
    
    print(f"\n🔓 User Login Process:")
    print(f"   1. User provides password: '{user_password}'")
    print(f"   2. System retrieves salt from database")
    print(f"   3. Regenerate keypair from password + salt")
    
    # Simulate login - regenerate keys
    regenerated_credentials = StarkCrypto.regenerate_key_pair_from_password(
        password=user_password,
        salt=salt,
        method="scrypt"
    )
    
    print(f"   4. Keys match: {credentials.private_key == regenerated_credentials.private_key}")
    print(f"   5. User can now sign transactions!")


if __name__ == "__main__":
    demo_password_keypair_generation()
    demo_use_cases()
    demo_integration_example()
    
    print("\n\n🎉 Demo Complete!")
    print("Your StarkCrypto class now supports password-based keypair generation!") 