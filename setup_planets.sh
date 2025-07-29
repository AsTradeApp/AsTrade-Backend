#!/bin/bash

# Setup script for AsTrade Planets System
# This script sets up the database schema and seeds the quiz data

echo "🌟 Setting up AsTrade Planets System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "planets_schema.sql" ]; then
    print_error "planets_schema.sql not found. Please run this script from the AsTrade-Backend directory."
    exit 1
fi

# Check if PLANET_QUIZES.md exists
if [ ! -f "PLANET_QUIZES.md" ]; then
    if [ -f "../PLANET_QUIZES.md" ]; then
        print_status "Copying PLANET_QUIZES.md from parent directory..."
        cp ../PLANET_QUIZES.md ./
    else
        print_error "PLANET_QUIZES.md not found. Please ensure this file exists."
        exit 1
    fi
fi

# Check environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    print_warning "SUPABASE_URL and SUPABASE_KEY environment variables not set."
    print_warning "Please ensure these are configured before running the backend."
fi

# Step 1: Check if Python dependencies are installed
print_status "Checking Python dependencies..."
if ! python -c "import supabase" 2>/dev/null; then
    print_warning "Supabase Python client not found. Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies. Please install manually: pip install -r requirements.txt"
        exit 1
    fi
fi

# Step 2: Apply database schema (if using Supabase CLI)
if command -v supabase &> /dev/null; then
    print_status "Applying database schema using Supabase CLI..."
    supabase db push
    if [ $? -eq 0 ]; then
        print_status "Database schema applied successfully!"
    else
        print_warning "Supabase CLI push failed. You may need to apply the schema manually."
        print_warning "Copy the contents of planets_schema.sql and execute in your Supabase SQL editor."
    fi
else
    print_warning "Supabase CLI not found."
    print_warning "Please apply the database schema manually:"
    print_warning "1. Open your Supabase project dashboard"
    print_warning "2. Go to SQL Editor"
    print_warning "3. Copy and execute the contents of planets_schema.sql"
    print_warning "Press Enter when you've completed this step..."
    read
fi

# Step 3: Seed the database with quiz data
print_status "Seeding database with quiz data..."
python seed_planets_data.py

if [ $? -eq 0 ]; then
    print_status "✅ Database seeded successfully!"
else
    print_error "❌ Database seeding failed. Please check the error messages above."
    exit 1
fi

# Step 4: Verification
print_status "Running verification checks..."

# Check if we can import the planets service
if python -c "from app.services.planets_service import planets_service; print('Planets service imported successfully')" 2>/dev/null; then
    print_status "✅ Planets service is properly configured"
else
    print_error "❌ Planets service import failed. Please check your configuration."
    exit 1
fi

echo ""
echo "🎉 Planets system setup completed successfully!"
echo ""
echo "📡 Available API endpoints:"
echo "  GET  /api/v1/planets/                    - List all planets"
echo "  GET  /api/v1/planets/{id}               - Get planet details"
echo "  GET  /api/v1/planets/quiz/{id}          - Get quiz details"
echo "  POST /api/v1/planets/quiz/{id}/start    - Start a quiz (auth required)"
echo "  POST /api/v1/planets/quiz/submit        - Submit quiz answers (auth required)"
echo "  GET  /api/v1/planets/progress/overview  - Get user progress (auth required)"
echo "  GET  /api/v1/planets/health             - Health check"
echo ""
echo "🚀 Next steps:"
echo "  1. Start your backend server: python run.py"
echo "  2. Test the endpoints using the API documentation at /docs"
echo "  3. Integrate with your frontend application"
echo ""
echo "📚 For detailed documentation, see: PLANETS_README.md" 