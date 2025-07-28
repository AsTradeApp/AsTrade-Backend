"""
Example: Extracting Keys from StarkPerpetualAccount

This example demonstrates how to obtain private key, public key, and API key
from a StarkPerpetualAccount instance.
"""

import asyncio
import logging
from x10.perpetual.accounts import StarkPerpetualAccount
from app.services.extended.sdk_config import TESTNET_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_account_keys(stark_account: StarkPerpetualAccount) -> dict:
    """
    Extract all key information from a StarkPerpetualAccount instance
    
    Args:
        stark_account: StarkPerpetualAccount instance
        
    Returns:
        Dictionary containing all extracted keys and account info
    """
    logger.info("Extracting keys from StarkPerpetualAccount...")
    
    # Extract all available properties
    account_data = {
        # Private key (as string)
        "private_key": stark_account.private_key,
        
        # Public key (as integer - convert to hex if needed)
        "public_key": stark_account.public_key,
        "public_key_hex": hex(stark_account.public_key),
        
        # API key (as string)
        "api_key": stark_account.api_key,
        
        # Vault ID (as integer)
        "vault": stark_account.vault,
    }
    
    # Log the extracted information (with partial keys for security)
    logger.info("✅ Successfully extracted account keys:")
    logger.info(f"  - Private Key: {account_data['private_key'][:10]}...{account_data['private_key'][-4:]}")
    logger.info(f"  - Public Key (hex): {account_data['public_key_hex'][:10]}...{account_data['public_key_hex'][-4:]}")
    logger.info(f"  - Public Key (int): {account_data['public_key']}")
    logger.info(f"  - API Key: {account_data['api_key'][:8]}...{account_data['api_key'][-4:]}")
    logger.info(f"  - Vault ID: {account_data['vault']}")
    
    return account_data


def demonstrate_key_extraction():
    """
    Demonstrate how to extract keys from a StarkPerpetualAccount
    """
    logger.info("=== StarkPerpetualAccount Key Extraction Example ===")
    
    # Sample account data (replace with your actual values)
    sample_data = {
        "vault": 500073,
        "private_key": "0x06e32701e1e23eb7d7556b940ce78dfda1587310e3b473bbda4720a566872bb4",
        "public_key": "0x01bc414ddd1ac27e15f587e73e05b742fa0f28e004cb9eed93fba7f898ff1618",
        "api_key": "b87ece7b7171c308f27ec4a18e30472d"
    }
    
    # Create StarkPerpetualAccount instance
    logger.info("Creating StarkPerpetualAccount...")
    stark_account = StarkPerpetualAccount(
        vault=sample_data["vault"],
        private_key=sample_data["private_key"],
        public_key=sample_data["public_key"],
        api_key=sample_data["api_key"]
    )
    
    # Extract all keys
    extracted_keys = extract_account_keys(stark_account)
    
    # Show different ways to access the data
    logger.info("\n📋 Different ways to access the extracted data:")
    
    # Method 1: Direct property access
    logger.info("1️⃣ Direct property access:")
    logger.info(f"   stark_account.private_key = {stark_account.private_key}")
    logger.info(f"   stark_account.public_key = {stark_account.public_key}")
    logger.info(f"   stark_account.api_key = {stark_account.api_key}")
    logger.info(f"   stark_account.vault = {stark_account.vault}")
    
    # Method 2: Using extracted dictionary
    logger.info("2️⃣ Using extracted dictionary:")
    logger.info(f"   Private Key: {extracted_keys['private_key']}")
    logger.info(f"   Public Key (hex): {extracted_keys['public_key_hex']}")
    logger.info(f"   Public Key (int): {extracted_keys['public_key']}")
    logger.info(f"   API Key: {extracted_keys['api_key']}")
    logger.info(f"   Vault: {extracted_keys['vault']}")
    
    # Method 3: Converting formats
    logger.info("3️⃣ Key format conversions:")
    
    # Convert private key from hex string to integer
    private_key_int = int(stark_account.private_key, 16)
    logger.info(f"   Private Key (int): {private_key_int}")
    
    # Convert public key from integer to hex string
    public_key_hex = hex(stark_account.public_key)
    logger.info(f"   Public Key (hex): {public_key_hex}")
    
    # Return the extracted data for further use
    return extracted_keys


def use_extracted_keys_for_new_account(extracted_keys: dict) -> StarkPerpetualAccount:
    """
    Demonstrate how to use extracted keys to create a new account
    """
    logger.info("\n🔄 Creating new account from extracted keys...")
    
    # Create new account using extracted data
    new_account = StarkPerpetualAccount(
        vault=extracted_keys["vault"],
        private_key=extracted_keys["private_key"],
        public_key=extracted_keys["public_key_hex"],  # Can use hex format
        api_key=extracted_keys["api_key"]
    )
    
    logger.info("✅ New account created successfully!")
    logger.info(f"   Vault: {new_account.vault}")
    logger.info(f"   Public Key: {hex(new_account.public_key)[:16]}...")
    logger.info(f"   API Key: {new_account.api_key[:8]}...")
    
    return new_account


if __name__ == "__main__":
    # Run the demonstration
    extracted_data = demonstrate_key_extraction()
    
    # Show how to use the extracted keys
    new_account = use_extracted_keys_for_new_account(extracted_data)
    
    logger.info("\n🎉 Key extraction example completed successfully!") 