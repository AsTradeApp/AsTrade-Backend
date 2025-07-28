#!/usr/bin/env python3
"""
Real Starknet Contract Deployment Script

This script actually deploys contracts to Starknet using starknet.py and the Cairo CLI.
Unlike the mock deployment, this performs real blockchain transactions.

Requirements:
    pip install starknet.py cairo-lang
    starknet-devnet (for local testing)

Usage:
    python scripts/real_deploy_contracts.py --network sepolia
    python scripts/real_deploy_contracts.py --network mainnet --private-key 0x123...
"""

import asyncio
import argparse
import os
import sys
import json
import subprocess
from typing import Optional, Dict, Any
from starknet_py.net import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.contract import Contract
from starknet_py.cairo.felt import encode_shortstring
from starknet_py.hash.selector import get_selector_from_name

class RealStarknetDeployer:
    """Real Starknet contract deployer using starknet.py"""
    
    def __init__(self, network: str, private_key: str):
        self.network = network
        self.private_key = private_key
        self.client = self._create_client(network)
        self.account = None
        self.deployments = {}
        
    def _create_client(self, network: str) -> GatewayClient:
        """Create real Starknet client"""
        if network == "sepolia":
            return GatewayClient(
                net="https://alpha4.starknet.io",
                chain=StarknetChainId.TESTNET
            )
        elif network == "mainnet":
            return GatewayClient(
                net="https://alpha-mainnet.starknet.io",
                chain=StarknetChainId.MAINNET
            )
        elif network == "devnet":
            return GatewayClient(
                net="http://127.0.0.1:5050",
                chain=StarknetChainId.TESTNET
            )
        else:
            raise ValueError(f"Unsupported network: {network}")
    
    async def setup_account(self, account_address: str) -> None:
        """Setup account for deployment"""
        print(f"🔐 Setting up deployer account...")
        print(f"   Address: {account_address}")
        print(f"   Network: {self.network}")
        
        signer = StarkCurveSigner(
            account_address=account_address,
            private_key=int(self.private_key, 16),
            chain_id=self.client.chain
        )
        
        self.account = Account(
            address=account_address,
            client=self.client,
            signer=signer
        )
        
        # Check account balance
        balance = await self.account.get_balance()
        print(f"   Balance: {balance / 10**18:.4f} ETH")
        
        if balance == 0:
            raise Exception("Account has no ETH for deployment fees")
        
        print("✅ Account setup complete")
    
    async def compile_cairo_contract(self, contract_path: str) -> Dict[str, Any]:
        """Compile Cairo contract using scarb"""
        print(f"🔨 Compiling {contract_path}...")
        
        # Change to contract directory
        original_dir = os.getcwd()
        contract_dir = os.path.join(original_dir, contract_path)
        
        try:
            os.chdir(contract_dir)
            
            # Run scarb build
            result = subprocess.run(
                ["scarb", "build"],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ Compilation successful")
            
            # Read compiled artifacts
            target_dir = os.path.join(contract_dir, "target", "dev")
            sierra_file = None
            casm_file = None
            
            for file in os.listdir(target_dir):
                if file.endswith(".contract_class.json"):
                    sierra_file = os.path.join(target_dir, file)
                elif file.endswith(".compiled_contract_class.json"):
                    casm_file = os.path.join(target_dir, file)
            
            if not sierra_file or not casm_file:
                raise Exception("Compiled artifacts not found")
            
            with open(sierra_file, 'r') as f:
                sierra_class = json.load(f)
            
            with open(casm_file, 'r') as f:
                casm_class = json.load(f)
            
            return {
                "sierra": sierra_class,
                "casm": casm_class
            }
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Compilation failed: {e.stderr}")
        finally:
            os.chdir(original_dir)
    
    async def deploy_contract(
        self, 
        contract_name: str,
        compiled_contract: Dict[str, Any],
        constructor_args: list
    ) -> Dict[str, Any]:
        """Deploy contract to Starknet"""
        print(f"🚀 Deploying {contract_name} to {self.network}...")
        
        # Declare contract class
        print("   📋 Declaring contract class...")
        declare_result = await self.account.sign_and_send_declare(
            compiled_contract=compiled_contract["sierra"],
            compiled_contract_casm=compiled_contract["casm"]
        )
        
        await self.client.wait_for_tx(declare_result.transaction_hash)
        class_hash = declare_result.class_hash
        print(f"   ✅ Class declared: {hex(class_hash)}")
        
        # Deploy contract instance
        print("   📦 Deploying contract instance...")
        deploy_result = await self.account.sign_and_send_deploy_account(
            class_hash=class_hash,
            constructor_calldata=constructor_args,
            salt=0
        )
        
        await self.client.wait_for_tx(deploy_result.transaction_hash)
        contract_address = deploy_result.contract_address
        print(f"   ✅ Contract deployed: {hex(contract_address)}")
        
        deployment_info = {
            "contract_name": contract_name,
            "contract_address": hex(contract_address),
            "class_hash": hex(class_hash),
            "transaction_hash": hex(deploy_result.transaction_hash),
            "network": self.network,
            "constructor_args": constructor_args,
            "deployed_at": deploy_result.block_number,
            "status": "deployed"
        }
        
        self.deployments[contract_name] = deployment_info
        return deployment_info
    
    async def deploy_xp_system(self, owner_address: str, xp_per_trade: int) -> Dict[str, Any]:
        """Deploy XP System contract"""
        print("🎯 Deploying XP System contract...")
        
        # Compile contract
        compiled = await self.compile_cairo_contract("contracts/streetcred_xp")
        
        # Constructor arguments: (owner, xp_per_trade)
        constructor_args = [
            int(owner_address, 16),
            xp_per_trade
        ]
        
        return await self.deploy_contract("xp_system", compiled, constructor_args)
    
    async def deploy_nft_contract(
        self, 
        owner_address: str,
        name: str = "StreetCred Achievement NFTs",
        symbol: str = "SCNFT"
    ) -> Dict[str, Any]:
        """Deploy NFT contract"""
        print("🎨 Deploying NFT contract...")
        
        # Compile contract
        compiled = await self.compile_cairo_contract("contracts/street_art_nft")
        
        # Constructor arguments: (name, symbol, owner)
        constructor_args = [
            encode_shortstring(name),
            encode_shortstring(symbol),
            int(owner_address, 16)
        ]
        
        return await self.deploy_contract("street_art_nft", compiled, constructor_args)
    
    async def deploy_paymaster(self, owner_address: str, initial_balance: int) -> Dict[str, Any]:
        """Deploy Paymaster contract"""
        print("💰 Deploying Paymaster contract...")
        
        # Compile contract
        compiled = await self.compile_cairo_contract("contracts/streetcred_paymaster")
        
        # Constructor arguments: (owner, initial_balance)
        constructor_args = [
            int(owner_address, 16),
            initial_balance
        ]
        
        return await self.deploy_contract("paymaster", compiled, constructor_args)
    
    async def setup_contract_permissions(self) -> None:
        """Setup permissions between deployed contracts"""
        print("🔧 Setting up contract permissions...")
        
        xp_deployment = self.deployments.get("xp_system")
        nft_deployment = self.deployments.get("street_art_nft")
        paymaster_deployment = self.deployments.get("paymaster")
        
        if not all([xp_deployment, nft_deployment]):
            raise Exception("XP and NFT contracts must be deployed first")
        
        # Create contract instances
        xp_contract = Contract(
            address=int(xp_deployment["contract_address"], 16),
            abi=[], # Would load from compilation artifacts
            provider=self.account
        )
        
        nft_contract = Contract(
            address=int(nft_deployment["contract_address"], 16),
            abi=[],
            provider=self.account
        )
        
        # Set NFT contract as authorized on XP contract
        print("   🔗 Authorizing NFT contract on XP contract...")
        call = await xp_contract.functions["set_authorized_contract"].invoke(
            contract_address=int(nft_deployment["contract_address"], 16),
            authorized=True
        )
        await self.client.wait_for_tx(call.transaction_hash)
        
        # Set XP contract as authorized minter on NFT contract
        print("   🔗 Authorizing XP contract on NFT contract...")
        call = await nft_contract.functions["set_authorized_minter"].invoke(
            minter_address=int(xp_deployment["contract_address"], 16),
            authorized=True
        )
        await self.client.wait_for_tx(call.transaction_hash)
        
        if paymaster_deployment:
            paymaster_contract = Contract(
                address=int(paymaster_deployment["contract_address"], 16),
                abi=[],
                provider=self.account
            )
            
            # Authorize contracts on paymaster
            print("   🔗 Authorizing contracts on paymaster...")
            for contract_name in ["xp_system", "street_art_nft"]:
                deployment = self.deployments[contract_name]
                call = await paymaster_contract.functions["set_authorized_contract"].invoke(
                    contract_address=int(deployment["contract_address"], 16),
                    authorized=True
                )
                await self.client.wait_for_tx(call.transaction_hash)
        
        print("✅ Contract permissions configured")
    
    async def verify_deployments(self) -> bool:
        """Verify deployed contracts are working"""
        print("🔍 Verifying deployments...")
        
        for contract_name, deployment in self.deployments.items():
            print(f"   📋 Verifying {contract_name}...")
            
            # Create contract instance
            contract = Contract(
                address=int(deployment["contract_address"], 16),
                abi=[],
                provider=self.account
            )
            
            # Basic verification calls
            if contract_name == "xp_system":
                # Try to read owner
                try:
                    result = await contract.functions["get_owner"].call()
                    print(f"     ✅ Owner: {hex(result[0])}")
                except Exception as e:
                    print(f"     ❌ Failed to read owner: {e}")
                    return False
            
            elif contract_name == "street_art_nft":
                # Try to read name and symbol
                try:
                    name_result = await contract.functions["name"].call()
                    symbol_result = await contract.functions["symbol"].call()
                    print(f"     ✅ Name: {name_result}")
                    print(f"     ✅ Symbol: {symbol_result}")
                except Exception as e:
                    print(f"     ❌ Failed to read NFT info: {e}")
                    return False
        
        print("✅ All contracts verified")
        return True
    
    def save_deployment_config(self) -> None:
        """Save deployment configuration for Flutter app"""
        print("💾 Saving deployment configuration...")
        
        # Create deployment directory
        os.makedirs(f"deployments/{self.network}", exist_ok=True)
        
        # Save individual deployments
        for contract_name, deployment in self.deployments.items():
            config_file = f"deployments/{self.network}/{contract_name}.json"
            with open(config_file, 'w') as f:
                json.dump(deployment, f, indent=2)
        
        # Create Flutter configuration
        config_file = "lib/config/real_contract_config.dart"
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        xp_address = self.deployments.get("xp_system", {}).get("contract_address", "")
        nft_address = self.deployments.get("street_art_nft", {}).get("contract_address", "")
        paymaster_address = self.deployments.get("paymaster", {}).get("contract_address", "")
        
        # Get real Starknet function selectors
        selectors = {
            "add_xp": hex(get_selector_from_name("add_xp")),
            "get_xp": hex(get_selector_from_name("get_xp")),
            "get_leaderboard_top_10": hex(get_selector_from_name("get_leaderboard_top_10")),
            "mint_achievement_nft": hex(get_selector_from_name("mint_achievement_nft")),
            "validate_paymaster_transaction": hex(get_selector_from_name("validate_paymaster_transaction"))
        }
        
        config_content = f'''/// Real Starknet Contract Configuration
/// Deployed to {self.network} with actual blockchain transactions

class RealContractConfig {{
  static const String network = "{self.network}";
  static const String rpcUrl = "{self.client.net}";
  
  // Real deployed contract addresses
  static const String xpContractAddress = "{xp_address}";
  static const String nftContractAddress = "{nft_address}";
  static const String paymasterContractAddress = "{paymaster_address}";
  
  // Real Starknet function selectors
  static const Map<String, String> functionSelectors = {{
    "add_xp": "{selectors['add_xp']}",
    "get_xp": "{selectors['get_xp']}",
    "get_leaderboard_top_10": "{selectors['get_leaderboard_top_10']}",
    "mint_achievement_nft": "{selectors['mint_achievement_nft']}",
    "validate_paymaster_transaction": "{selectors['validate_paymaster_transaction']}",
  }};
  
  // Deployment information
  static const Map<String, Map<String, dynamic>> deployments = {json.dumps(self.deployments, indent=4)};
}}
'''
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Configuration saved to {config_file}")

async def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy contracts to real Starknet")
    parser.add_argument("--network", choices=["sepolia", "mainnet", "devnet"], 
                       default="sepolia", help="Starknet network")
    parser.add_argument("--private-key", required=True, 
                       help="Private key for deployment account")
    parser.add_argument("--account-address", required=True,
                       help="Address of deployment account")
    parser.add_argument("--skip-paymaster", action="store_true",
                       help="Skip paymaster deployment")
    
    args = parser.parse_args()
    
    print("🏗️  Real Starknet Contract Deployment")
    print("=" * 60)
    print(f"Network: {args.network}")
    print(f"Account: {args.account_address}")
    print()
    
    deployer = RealStarknetDeployer(args.network, args.private_key)
    
    try:
        # Setup deployment account
        await deployer.setup_account(args.account_address)
        
        # Deploy XP System
        xp_deployment = await deployer.deploy_xp_system(args.account_address, 25)
        
        # Deploy NFT contract
        nft_deployment = await deployer.deploy_nft_contract(args.account_address)
        
        # Deploy paymaster (optional)
        if not args.skip_paymaster:
            paymaster_deployment = await deployer.deploy_paymaster(
                args.account_address, 
                1000000000000000000  # 1 ETH initial balance
            )
        
        # Setup permissions
        await deployer.setup_contract_permissions()
        
        # Verify deployments
        await deployer.verify_deployments()
        
        # Save configuration
        deployer.save_deployment_config()
        
        print()
        print("🎉 Real Starknet Deployment Complete!")
        print("=" * 60)
        print(f"✅ XP System: {xp_deployment['contract_address']}")
        print(f"✅ NFT Contract: {nft_deployment['contract_address']}")
        if not args.skip_paymaster:
            paymaster_deployment = deployer.deployments.get("paymaster")
            if paymaster_deployment:
                print(f"✅ Paymaster: {paymaster_deployment['contract_address']}")
        print(f"✅ Network: {args.network}")
        print("✅ Contracts are live on Starknet blockchain!")
        
    except Exception as e:
        print(f"❌ Real deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())