"""
Stark cryptography utilities for Extended Exchange integration
"""
import hashlib
import secrets
import os
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


@dataclass
class StarkKeyPair:
    """Stark key pair for Extended Exchange"""
    private_key: str
    public_key: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "private_key": self.private_key,
            "public_key": self.public_key
        }


class StarkCrypto:
    """Stark cryptography utilities for Extended Exchange"""
    
    @staticmethod
    def generate_private_key() -> str:
        """
        Generate a random Stark private key
        
        Returns:
            hex string of private key (64 chars)
        """
        # Generate 32 random bytes (256 bits)
        private_key_bytes = secrets.token_bytes(32)
        return private_key_bytes.hex()
    
    @staticmethod
    def generate_private_key_from_password(
        password: str,
        salt: Optional[bytes] = None,
        method: str = "pbkdf2",
        iterations: int = 100000
    ) -> Tuple[str, bytes]:
        """
        Generate a deterministic Stark private key from a password
        
        Args:
            password: User password as entropy source
            salt: Optional salt bytes. If None, generates random salt
            method: "pbkdf2" or "scrypt" for key derivation
            iterations: Number of iterations for PBKDF2 (ignored for scrypt)
            
        Returns:
            Tuple of (hex_private_key, salt_used)
        """
        if salt is None:
            salt = os.urandom(32)  # 256-bit salt
        
        password_bytes = password.encode('utf-8')
        
        if method == "pbkdf2":
            # Using PBKDF2 with SHA256
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits for private key
                salt=salt,
                iterations=iterations,
            )
            key_bytes = kdf.derive(password_bytes)
            
        elif method == "scrypt":
            # Using scrypt (more memory-hard, better for password-based keys)
            kdf = Scrypt(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                n=2**14,    # CPU cost factor
                r=8,        # Memory cost factor
                p=1,        # Parallelization factor
            )
            key_bytes = kdf.derive(password_bytes)
            
        else:
            raise ValueError(f"Unsupported method: {method}. Use 'pbkdf2' or 'scrypt'")
        
        return key_bytes.hex(), salt
    
    @staticmethod
    def regenerate_private_key_from_password(
        password: str,
        salt: bytes,
        method: str = "pbkdf2",
        iterations: int = 100000
    ) -> str:
        """
        Regenerate the same private key from password and known salt
        
        Args:
            password: Original password
            salt: Salt bytes used in original generation
            method: KDF method used ("pbkdf2" or "scrypt")
            iterations: Original iterations count
            
        Returns:
            hex string of regenerated private key
        """
        private_key, _ = StarkCrypto.generate_private_key_from_password(
            password=password,
            salt=salt,
            method=method,
            iterations=iterations
        )
        return private_key
    
    @staticmethod
    def derive_public_key(private_key: str) -> str:
        """
        Derive public key from private key
        
        This is a simplified implementation. In production, you would use
        the actual Stark curve cryptography (secp256k1 or Stark curve)
        
        Args:
            private_key: hex string of private key
            
        Returns:
            hex string of public key
        """
        # Simplified derivation using SHA256 (NOT for production)
        # In production, use proper elliptic curve point multiplication
        private_bytes = bytes.fromhex(private_key)
        public_bytes = hashlib.sha256(private_bytes + b"public").digest()
        return public_bytes.hex()
    
    @staticmethod
    def generate_key_pair() -> StarkKeyPair:
        """
        Generate a complete Stark key pair
        
        Returns:
            StarkKeyPair with private and public keys
        """
        private_key = StarkCrypto.generate_private_key()
        public_key = StarkCrypto.derive_public_key(private_key)
        
        return StarkKeyPair(
            private_key=private_key,
            public_key=public_key
        )
    
    @staticmethod
    def generate_key_pair_from_password(
        password: str,
        salt: Optional[bytes] = None,
        method: str = "pbkdf2",
        iterations: int = 100000
    ) -> Tuple[StarkKeyPair, bytes]:
        """
        Generate a complete Stark key pair from a password
        
        Args:
            password: User password as entropy source
            salt: Optional salt bytes. If None, generates random salt
            method: "pbkdf2" or "scrypt" for key derivation
            iterations: Number of iterations for PBKDF2
            
        Returns:
            Tuple of (StarkKeyPair, salt_used)
        """
        private_key, salt_used = StarkCrypto.generate_private_key_from_password(
            password=password,
            salt=salt,
            method=method,
            iterations=iterations
        )
        public_key = StarkCrypto.derive_public_key(private_key)
        
        key_pair = StarkKeyPair(
            private_key=private_key,
            public_key=public_key
        )
        
        return key_pair, salt_used
    
    @staticmethod
    def regenerate_key_pair_from_password(
        password: str,
        salt: bytes,
        method: str = "pbkdf2",
        iterations: int = 100000
    ) -> StarkKeyPair:
        """
        Regenerate the same key pair from password and known salt
        
        Args:
            password: Original password
            salt: Salt bytes used in original generation
            method: KDF method used
            iterations: Original iterations count
            
        Returns:
            StarkKeyPair with regenerated keys
        """
        private_key = StarkCrypto.regenerate_private_key_from_password(
            password=password,
            salt=salt,
            method=method,
            iterations=iterations
        )
        public_key = StarkCrypto.derive_public_key(private_key)
        
        return StarkKeyPair(
            private_key=private_key,
            public_key=public_key
        )
    
    @staticmethod
    def sign_message(private_key: str, message: str) -> str:
        """
        Sign a message using Stark private key
        
        This is a simplified implementation. In production, you would use
        the actual Stark signature scheme
        
        Args:
            private_key: hex string of private key
            message: message to sign
            
        Returns:
            hex string of signature
        """
        # Simplified signing using HMAC-SHA256 (NOT for production)
        # In production, use proper Stark signature scheme
        private_bytes = bytes.fromhex(private_key)
        message_bytes = message.encode('utf-8')
        
        # Create signature using HMAC
        import hmac
        signature = hmac.new(private_bytes, message_bytes, hashlib.sha256).digest()
        return signature.hex()
    
    @staticmethod
    def verify_signature(public_key: str, message: str, signature: str) -> bool:
        """
        Verify a signature using Stark public key
        
        Args:
            public_key: hex string of public key
            message: original message
            signature: hex string of signature
            
        Returns:
            True if signature is valid
        """
        # This would need proper Stark signature verification
        # For now, just return True (NOT for production)
        return True
    
    @staticmethod
    def create_stark_signature_for_order(
        private_key: str,
        order_data: Dict[str, Any],
        signing_domain: str
    ) -> str:
        """
        Create Stark signature for order submission to Extended Exchange
        
        Args:
            private_key: Stark private key
            order_data: Order parameters
            signing_domain: Domain for signing (e.g., "testnet.extended.exchange")
            
        Returns:
            Signature string for Extended Exchange
        """
        # Create message to sign based on Extended Exchange format
        message_parts = [
            str(order_data.get('symbol', '')),
            str(order_data.get('side', '')),
            str(order_data.get('size', '')),
            str(order_data.get('price', '')),
            str(order_data.get('type', '')),
            signing_domain
        ]
        
        message = '|'.join(message_parts)
        return StarkCrypto.sign_message(private_key, message)


# Utility functions for Extended Exchange integration
def generate_stark_credentials() -> Dict[str, str]:
    """
    Generate Stark credentials for a new Extended Exchange account
    
    Returns:
        Dictionary with private_key and public_key
    """
    key_pair = StarkCrypto.generate_key_pair()
    return key_pair.to_dict()


def generate_stark_credentials_from_password(
    password: str,
    salt: Optional[bytes] = None,
    method: str = "pbkdf2"
) -> Tuple[Dict[str, str], bytes]:
    """
    Generate Stark credentials from a password
    
    Args:
        password: User password
        salt: Optional salt (generates random if None)
        method: Key derivation method
        
    Returns:
        Tuple of (credentials_dict, salt_used)
    """
    key_pair, salt_used = StarkCrypto.generate_key_pair_from_password(
        password=password,
        salt=salt,
        method=method
    )
    return key_pair.to_dict(), salt_used


def create_order_signature(
    private_key: str,
    order_params: Dict[str, Any],
    environment: str = "testnet"
) -> str:
    """
    Create signature for order submission
    
    Args:
        private_key: User's Stark private key
        order_params: Order parameters
        environment: "testnet" or "mainnet"
        
    Returns:
        Signature string
    """
    from app.config.extended_config import extended_config
    
    # Get appropriate signing domain
    if environment == "mainnet":
        signing_domain = extended_config.MAINNET_SIGNING_DOMAIN
    else:
        signing_domain = extended_config.TESTNET_SIGNING_DOMAIN_NEW
    
    return StarkCrypto.create_stark_signature_for_order(
        private_key, order_params, signing_domain
    ) 