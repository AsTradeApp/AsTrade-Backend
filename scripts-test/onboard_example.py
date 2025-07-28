import asyncio
import logging
from decimal import Decimal

from eth_account import Account
from eth_account.signers.local import LocalAccount

from x10.perpetual.accounts import StarkPerpetualAccount
from x10.perpetual.assets import AssetOperationType
from app.services.extended.sdk_config import TESTNET_CONFIG
from x10.perpetual.contract import call_erc20_approve, call_stark_perpetual_deposit
from x10.perpetual.trading_client.trading_client import PerpetualTradingClient
from x10.perpetual.user_client.user_client import UserClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# flake8: noqa
async def on_board_example():
    logger.info("Starting onboard example...")
    environment_config = TESTNET_CONFIG
    eth_account: LocalAccount = Account.from_key("0x0641234e542c48b9f50d7bb2e311d2b6aac4cec68d5b6da37c2258b82156e691")
    logger.info(f"Created eth_account with address: {eth_account.address}")
    logger.info("Creating user client...")
    user_client = UserClient(endpoint_config=environment_config, l1_private_key=eth_account.key.hex)
    
    logger.info("Onboarding user...")
    onboarded_user = await user_client.onboard()
    logger.info(f"User onboarded successfully. L2 Vault: {onboarded_user.account.l2_vault}")
    
    logger.info("Onboarding sub account 1...")
    sub_account_1 = await user_client.onboard_subaccount(1, "sub account 1")
    logger.info(f"Sub account 1 onboarded. L2 Vault: {sub_account_1.account.l2_vault}")

    logger.info("Creating API keys...")
    default_api_key = await user_client.create_account_api_key(onboarded_user.account, "trading api key")
    logger.info(f"Default API key created: {default_api_key[:8]}...")
    
    account_1_api_key = await user_client.create_account_api_key(sub_account_1.account, "sub account 1 api key")
    logger.info(f"Sub account 1 API key created: {account_1_api_key[:8]}...")

    logger.info("Creating default account trading client...")
    logger.info(f"  - Vault: {onboarded_user.account.l2_vault}")
    logger.info(f"  - Public Key: {onboarded_user.l2_key_pair.public_hex[:16]}...")
    logger.info(f"  - API Key: {default_api_key[:8]}...")
    
    try:
        default_account_trading_client = PerpetualTradingClient(
            environment_config,
            StarkPerpetualAccount(
                vault=onboarded_user.account.l2_vault,
                private_key=onboarded_user.l2_key_pair.private_hex,
                public_key=onboarded_user.l2_key_pair.public_hex,
                api_key=default_api_key,
            ),
        )
        logger.info("✅ Default account trading client created successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to create default account trading client: {e}")
        raise

    logger.info("Creating sub account 1 trading client...")
    logger.info(f"  - Vault: {sub_account_1.account.l2_vault}")
    logger.info(f"  - Public Key: {sub_account_1.l2_key_pair.public_hex[:16]}...")
    logger.info(f"  - API Key: {account_1_api_key[:8]}...")
    
    sub_account_1_trading_client = PerpetualTradingClient(
        environment_config,
        StarkPerpetualAccount(
            vault=sub_account_1.account.l2_vault,
            private_key=sub_account_1.l2_key_pair.private_hex,
            public_key=sub_account_1.l2_key_pair.public_hex,
            api_key=account_1_api_key,
        ),
    )
    logger.info("✅ Sub account 1 trading client created successfully!")

    logger.info("Approving ERC20 tokens for deposit (1000 tokens)...")
    call_erc20_approve(
        human_readable_amount=Decimal("1000"), get_eth_private_key=eth_account.key.hex, config=environment_config
    )
    logger.info("✅ ERC20 approval completed!")

    logger.info("Depositing funds to default account (1000 tokens)...")
    await default_account_trading_client.account.deposit(
        human_readable_amount=Decimal("1000"),
        get_eth_private_key=eth_account.key.hex,
    )
    logger.info("✅ Deposit completed!")

    logger.info(f"Transferring 10 tokens from default account to sub account 1 (vault: {sub_account_1.account.l2_vault})...")
    default_account_trading_client.account.transfer(
        to_vault=int(sub_account_1.account.l2_vault),
        to_l2_key=sub_account_1.l2_key_pair.public_hex,
        amount=Decimal("10"),
    )
    logger.info("✅ Transfer completed!")

    logger.info(f"Creating slow withdrawal of 10 tokens to {eth_account.address}...")
    created_withdrawal_id = await default_account_trading_client.account.slow_withdrawal(
        amount=Decimal("10"),
        eth_address=eth_account.address,
    )
    logger.info(f"✅ Slow withdrawal created with ID: {created_withdrawal_id}")

    logger.info("Fetching withdrawal operations...")
    withdrawals = await default_account_trading_client.account.asset_operations(
        operations_type=[AssetOperationType.SLOW_WITHDRAWAL],
    )
    logger.info(f"Found {len(withdrawals)} withdrawal operations")

    logger.info("⏳ Waiting for withdrawal to be ready for claim...")

    logger.info("Checking available L1 withdrawal balance...")
    available_withdrawal_balance = await user_client.available_l1_withdrawal_balance()
    logger.info(f"Available withdrawal balance: {available_withdrawal_balance}")

    logger.info("Performing L1 withdrawal...")
    withdrawal_tx_hash = await user_client.perform_l1_withdrawal()
    logger.info(f"✅ L1 withdrawal completed! TX Hash: {withdrawal_tx_hash}")

    logger.info("🎉 Onboarding example completed successfully!")


asyncio.run(on_board_example())