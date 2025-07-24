"""
Stark cryptography utilities for Extended Exchange integration
"""
import hashlib
import secrets
from typing import Tuple, Dict, Any
from dataclasses import dataclass


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