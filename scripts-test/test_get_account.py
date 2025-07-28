import asyncio
import logging
import os
import aiohttp
from dotenv import load_dotenv

from x10.perpetual.accounts import StarkPerpetualAccount
from app.services.extended.sdk_config import TESTNET_CONFIG
from x10.perpetual.trading_client import PerpetualTradingClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("get_l2_account_info")

load_dotenv()

# Use your existing L2/Starknet credentials
API_KEY = os.getenv("X10_API_KEY", "65e33a7ac37b6e3e21189230eb7a102d")
PUBLIC_KEY = os.getenv("X10_PUBLIC_KEY", "0x01bc414ddd1ac27e15f587e73e05b742fa0f28e004cb9eed93fba7f898ff1618")
PRIVATE_KEY = os.getenv("X10_PRIVATE_KEY", "0x6e32701e1e23eb7d7556b940ce78dfda1587310e3b473bbda4720a566872bb4")


async def get_account_info_via_api():
    """Get account information using direct API calls with existing L2 credentials"""
    logger.info("=== L2 ACCOUNT INFORMATION TOOL ===")
    logger.info("Getting account info using existing L2 credentials and API key...")
    
    base_url = "https://api.starknet.sepolia.extended.exchange/api/v1"
    headers = {
        "X-Api-Key": API_KEY,
        "Accept": "application/json",
        "User-Agent": "AsTrade/1.0.0 (compatible; MyApp/1.0; +https://extended.exchange)"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Try to get account balance first (this usually works if credentials are correct)
            logger.info("Getting account balance...")
            async with session.get(f"{base_url}/user/balance", headers=headers) as response:
                if response.status == 200:
                    balance_data = await response.json()
                    logger.info("✅ Balance retrieved successfully!")
                    logger.info(f"Balance: {balance_data}")
                else:
                    logger.error(f"Failed to get balance: {response.status} - {await response.text()}")
                    return
            
            # Try to get positions
            logger.info("Getting positions...")
            async with session.get(f"{base_url}/user/positions", headers=headers) as response:
                if response.status == 200:
                    positions_data = await response.json()
                    logger.info("✅ Positions retrieved successfully!")
                    logger.info(f"Positions: {positions_data}")
                else:
                    logger.warning(f"Could not get positions: {response.status}")
            
            # Try to get account details
            logger.info("Getting account details...")
            async with session.get(f"{base_url}/user/account", headers=headers) as response:
                if response.status == 200:
                    account_data = await response.json()
                    logger.info("✅ Account details retrieved!")
                    logger.info(f"Account: {account_data}")
                    
                    # Extract vault ID if available
                    if account_data.get("data"):
                        if isinstance(account_data["data"], dict):
                            vault_id = account_data["data"].get("id") or account_data["data"].get("vault_id") or account_data["data"].get("account_id")
                            if vault_id:
                                logger.info(f"🎯 Found Vault ID: {vault_id}")
                else:
                    logger.warning(f"Could not get account details: {response.status}")
            
            # Try user profile endpoint
            logger.info("Getting user profile...")
            async with session.get(f"{base_url}/user", headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    logger.info("✅ User profile retrieved!")
                    logger.info(f"User: {user_data}")
                else:
                    logger.warning(f"Could not get user profile: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error during API calls: {e}")


async def test_vault_ids_with_l2_credentials():
    """Test different vault IDs using your L2 credentials"""
    logger.info("\n=== TESTING VAULT IDs WITH L2 CREDENTIALS ===")
    
    # Test common vault ID patterns
    test_vault_ids = [500060, 500071, 500072, 500073, 500074, 500075, 500076, 500077, 500078, 500079, 500080]
    
    for vault_id in test_vault_ids:
        try:
            logger.info(f"Testing vault ID: {vault_id}")
            
            stark_account = StarkPerpetualAccount(
                vault=vault_id,
                private_key=PRIVATE_KEY,
                public_key=PUBLIC_KEY,
                api_key=API_KEY,
            )
            
            trading_client = PerpetualTradingClient(
                endpoint_config=TESTNET_CONFIG,
                stark_account=stark_account,
            )
            
            # Try to get balance - this will fail if vault ID is wrong
            balance = await trading_client.account.get_balance()
            logger.info(f"🎉 SUCCESS! Vault ID {vault_id} works!")
            logger.info(f"Balance: {balance.to_pretty_json()}")
            
            # Also try to get positions to double-check
            positions = await trading_client.account.get_positions()
            logger.info(f"Positions: {positions.to_pretty_json()}")
            
            logger.info(f"\n✅ FOUND YOUR VAULT ID: {vault_id}")
            logger.info(f"🔑 Your complete L2 account info:")
            logger.info(f"   X10_VAULT_ID={vault_id}")
            logger.info(f"   X10_PRIVATE_KEY={PRIVATE_KEY}")
            logger.info(f"   X10_PUBLIC_KEY={PUBLIC_KEY}")
            logger.info(f"   X10_API_KEY={API_KEY}")
            
            return vault_id
            
        except Exception as e:
            error_msg = str(e)
            if "Invalid StarkEx vault" in error_msg:
                logger.info(f"   ❌ Vault ID {vault_id} invalid")
            else:
                logger.info(f"   ❌ Vault ID {vault_id} failed: {error_msg[:100]}...")
            continue
    
    logger.error("❌ None of the test vault IDs worked with your L2 credentials")
    return None


async def extract_vault_from_existing_credentials():
    """
    Since you've been successfully getting balance/positions with some vault ID,
    let's see what vault ID is actually in your current setup
    """
    logger.info("\n=== CHECKING YOUR CURRENT CREDENTIALS ===")
    
    # Check what vault ID you might be using in environment or defaults
    current_vault = os.getenv("X10_VAULT_ID")
    if current_vault:
        logger.info(f"Found X10_VAULT_ID in environment: {current_vault}")
        
        try:
            vault_id = int(current_vault)
            logger.info(f"Testing your environment vault ID: {vault_id}")
            
            stark_account = StarkPerpetualAccount(
                vault=vault_id,
                private_key=PRIVATE_KEY,
                public_key=PUBLIC_KEY,
                api_key=API_KEY,
            )
            
            trading_client = PerpetualTradingClient(
                endpoint_config=TESTNET_CONFIG,
                stark_account=stark_account,
            )
            
            balance = await trading_client.account.get_balance()
            logger.info(f"✅ Your environment vault ID {vault_id} works!")
            logger.info(f"Balance: {balance.to_pretty_json()}")
            return vault_id
            
        except Exception as e:
            logger.error(f"Your environment vault ID {current_vault} failed: {e}")
    else:
        logger.info("No X10_VAULT_ID found in environment")
    
    return None


async def main():
    logger.info("=== L2/STARKNET ACCOUNT DISCOVERY TOOL ===")
    logger.info("This tool is designed for accounts created with L2/Starknet wallets (like Cavos)")
    
    # First, check if you have a working vault ID in your environment
    working_vault = await extract_vault_from_existing_credentials()
    if working_vault:
        logger.info(f"\n🎉 Found working vault ID from your environment: {working_vault}")
        return
    
    # Get account info via API calls
    await get_account_info_via_api()
    
    # Test vault IDs with L2 credentials
    working_vault = await test_vault_ids_with_l2_credentials()
    
    if working_vault:
        logger.info(f"\n🎉 Success! Your vault ID is: {working_vault}")
        logger.info("Update your .env file with:")
        logger.info(f"X10_VAULT_ID={working_vault}")
    else:
        logger.error("\n❌ Could not find working vault ID")
        logger.info("\n💡 Possible solutions:")
        logger.info("1. Check your Extended Exchange account dashboard for vault ID")
        logger.info("2. Verify your API key has the correct permissions")
        logger.info("3. Make sure you're on the correct network (testnet/mainnet)")
        logger.info("4. Contact Extended Exchange support with your API key")


if __name__ == "__main__":
    asyncio.run(main())
