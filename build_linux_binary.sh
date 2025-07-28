#!/bin/bash

echo "🔨 Building Linux binary for Docker..."
echo "======================================"

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "⚠️  Warning: You're on macOS but building for Linux"
    echo "This will create a Linux-compatible binary for Docker"
fi

# Go to the consolidated directory
cd stark-crypto-consolidated

# Build for Linux target
echo "📦 Building with maturin for Linux..."
maturin build --release --target x86_64-unknown-linux-gnu

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Copy the Linux wheel to the python directory
    echo "📋 Copying Linux binary..."
    cp target/x86_64-unknown-linux-gnu/release/wheels/fast_stark_crypto-*.whl python/fast_stark_crypto/
    
    echo "🎉 Linux binary ready for Docker!"
    echo "📁 Binary location: python/fast_stark_crypto/"
else
    echo "❌ Build failed!"
    exit 1
fi 