#!/bin/bash

echo "🚀 Simple Docker Test for StarkNet Integration"
echo "=============================================="

# Step 1: Build Linux binary
echo "🔨 Step 1: Building Linux binary..."
./build_linux_binary.sh

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Linux binary"
    exit 1
fi

# Step 2: Build Docker image (much faster now)
echo ""
echo "🐳 Step 2: Building Docker image..."
docker-compose build api

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

# Step 3: Test the integration
echo ""
echo "🧪 Step 3: Testing StarkNet integration..."
docker-compose run --rm api python test_docker_starknet.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Everything works with Docker!"
    echo "✅ No Rust compilation in Docker"
    echo "✅ Lightweight image"
    echo "✅ StarkNet integration working"
    echo ""
    echo "🚀 Ready to run: docker-compose up"
else
    echo ""
    echo "❌ Test failed"
    exit 1
fi 