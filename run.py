#!/usr/bin/env python3
"""
AsTrade Backend Startup Script
Simplifies running the application with different configurations
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

def load_env_file(env_file=".env"):
    """Load environment variables from file"""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"⚠️  Environment file {env_file} not found")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import httpx
        import structlog
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def run_server(host="0.0.0.0", port=8000, reload=True, env="testnet"):
    """Run the FastAPI server"""
    os.environ["EXTENDED_ENVIRONMENT"] = env
    
    if not check_dependencies():
        sys.exit(1)
    
    print(f"🚀 Starting AsTrade Backend")
    print(f"📍 Environment: {env}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"🔄 Reload: {reload}")
    print("-" * 50)
    
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

def run_tests():
    """Run tests"""
    if not os.path.exists("app/tests"):
        print("⚠️  No tests directory found")
        return
    
    try:
        import pytest
        print("🧪 Running tests...")
        subprocess.run([sys.executable, "-m", "pytest", "app/tests/", "-v"])
    except ImportError:
        print("❌ pytest not installed. Run: pip install pytest")

def setup_database():
    """Setup database using docker-compose"""
    print("🗄️  Setting up database...")
    try:
        subprocess.run(["docker-compose", "up", "-d", "postgres", "redis"], check=True)
        print("✅ Database services started")
    except subprocess.CalledProcessError:
        print("❌ Failed to start database services")
        print("💡 Make sure Docker is running")

def main():
    parser = argparse.ArgumentParser(description="AsTrade Backend Runner")
    parser.add_argument("command", choices=["run", "test", "setup-db"], help="Command to execute")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--env", default="testnet", choices=["testnet", "mainnet"], help="Extended Exchange environment")
    parser.add_argument("--env-file", default=".env", help="Environment file to load")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_env_file(args.env_file)
    
    if args.command == "run":
        run_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
            env=args.env
        )
    elif args.command == "test":
        run_tests()
    elif args.command == "setup-db":
        setup_database()

if __name__ == "__main__":
    main() 