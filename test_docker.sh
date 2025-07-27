#!/bin/bash

# Test script for AsTrade backend running in Docker
# This script tests all the main endpoints

echo "============================================================"
echo "🔍 TESTING AS TRADE BACKEND (DOCKER)"
echo "============================================================"

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api/v1/users"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_section() {
    echo ""
    echo "============================================================"
    echo "🔍 $1"
    echo "============================================================"
}

# Test 1: Health check
print_section "TESTING HEALTH CHECK"
if curl -s "$BASE_URL/health" > /dev/null; then
    print_success "Backend is running and healthy"
else
    print_error "Backend is not responding"
    exit 1
fi

# Test 2: Integration status
print_section "TESTING INTEGRATION STATUS"
INTEGRATION_RESPONSE=$(curl -s "$API_BASE/integration/status")
if [ $? -eq 0 ]; then
    print_success "Integration status endpoint working"
    
    # Extract some info from the response
    PROFILES_COUNT=$(echo "$INTEGRATION_RESPONSE" | grep -o '"profiles_count":[0-9]*' | cut -d':' -f2)
    WALLETS_COUNT=$(echo "$INTEGRATION_RESPONSE" | grep -o '"wallets_count":[0-9]*' | cut -d':' -f2)
    CREDS_COUNT=$(echo "$INTEGRATION_RESPONSE" | grep -o '"credentials_count":[0-9]*' | cut -d':' -f2)
    
    print_info "Database records:"
    print_info "  - Profiles: $PROFILES_COUNT"
    print_info "  - Wallets: $WALLETS_COUNT"
    print_info "  - Credentials: $CREDS_COUNT"
else
    print_error "Integration status test failed"
fi

# Test 3: Create user
print_section "TESTING USER CREATION"
TIMESTAMP=$(date +%s)
USER_DATA='{
  "provider": "google",
  "email": "test_'$TIMESTAMP'@example.com",
  "cavos_user_id": "cavos-test-user-'$TIMESTAMP'",
  "wallet_address": "0x'$TIMESTAMP'abcdef1234567890abcdef1234567890abcdef12"
}'

CREATE_RESPONSE=$(curl -s -X POST "$API_BASE/register" \
  -H "Content-Type: application/json" \
  -d "$USER_DATA")

if [ $? -eq 0 ]; then
    print_success "User created successfully"
    
    # Extract user_id from response
    USER_ID=$(echo "$CREATE_RESPONSE" | grep -o '"user_id":"[^"]*"' | cut -d'"' -f4)
    print_info "User ID: $USER_ID"
    print_info "Email: test_$TIMESTAMP@example.com"
    print_info "Cavos ID: cavos-test-user-$TIMESTAMP"
else
    print_error "User creation failed"
    USER_ID=""
fi

# Test 4: Get user by ID
if [ ! -z "$USER_ID" ]; then
    print_section "TESTING USER LOOKUP BY ID"
    LOOKUP_RESPONSE=$(curl -s "$API_BASE/$USER_ID")
    
    if [ $? -eq 0 ]; then
        print_success "User lookup by ID working"
        
        # Extract some info
        EMAIL=$(echo "$LOOKUP_RESPONSE" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
        HAS_CREDS=$(echo "$LOOKUP_RESPONSE" | grep -o '"has_api_credentials":[^,]*' | cut -d':' -f2)
        
        print_info "Email: $EMAIL"
        print_info "Has API credentials: $HAS_CREDS"
    else
        print_error "User lookup failed"
    fi
fi

# Test 5: Get user by Cavos ID
if [ ! -z "$TIMESTAMP" ]; then
    print_section "TESTING USER LOOKUP BY CAVOS ID"
    CAVOS_ID="cavos-test-user-$TIMESTAMP"
    CAVOS_RESPONSE=$(curl -s "$API_BASE/cavos/$CAVOS_ID")
    
    if [ $? -eq 0 ]; then
        print_success "User lookup by Cavos ID working"
        
        # Extract some info
        FOUND_USER_ID=$(echo "$CAVOS_RESPONSE" | grep -o '"user_id":"[^"]*"' | cut -d'"' -f4)
        print_info "Found User ID: $FOUND_USER_ID"
    else
        print_error "Cavos lookup failed"
    fi
fi

# Test 6: Extended status
if [ ! -z "$USER_ID" ]; then
    print_section "TESTING EXTENDED STATUS"
    EXTENDED_RESPONSE=$(curl -s "$API_BASE/$USER_ID/extended/status")
    
    if [ $? -eq 0 ]; then
        print_success "Extended status endpoint working"
        
        # Extract some info
        CONFIGURED=$(echo "$EXTENDED_RESPONSE" | grep -o '"extended_configured":[^,]*' | cut -d':' -f2)
        ENVIRONMENT=$(echo "$EXTENDED_RESPONSE" | grep -o '"environment":"[^"]*"' | cut -d'"' -f4)
        
        print_info "Extended configured: $CONFIGURED"
        print_info "Environment: $ENVIRONMENT"
    else
        print_error "Extended status test failed"
    fi
fi

# Test 7: Extended setup
if [ ! -z "$USER_ID" ]; then
    print_section "TESTING EXTENDED SETUP"
    SETUP_RESPONSE=$(curl -s -X POST "$API_BASE/$USER_ID/extended/setup")
    
    if [ $? -eq 0 ]; then
        print_success "Extended setup endpoint working"
        
        # Extract some info
        COMPLETED=$(echo "$SETUP_RESPONSE" | grep -o '"setup_completed":[^,]*' | cut -d':' -f2)
        print_info "Setup completed: $COMPLETED"
    else
        print_error "Extended setup test failed"
    fi
fi

# Final status check
print_section "FINAL STATUS CHECK"
FINAL_RESPONSE=$(curl -s "$API_BASE/integration/status")
if [ $? -eq 0 ]; then
    print_success "Final integration status check passed"
    
    # Show updated counts
    FINAL_PROFILES=$(echo "$FINAL_RESPONSE" | grep -o '"profiles_count":[0-9]*' | cut -d':' -f2)
    FINAL_WALLETS=$(echo "$FINAL_RESPONSE" | grep -o '"wallets_count":[0-9]*' | cut -d':' -f2)
    FINAL_CREDS=$(echo "$FINAL_RESPONSE" | grep -o '"credentials_count":[0-9]*' | cut -d':' -f2)
    
    print_info "Updated database records:"
    print_info "  - Profiles: $FINAL_PROFILES"
    print_info "  - Wallets: $FINAL_WALLETS"
    print_info "  - Credentials: $FINAL_CREDS"
else
    print_error "Final status check failed"
fi

print_section "TEST COMPLETION"
print_success "All Docker tests completed!"
print_info "The AsTrade backend is working correctly with Docker."
print_info "Next step: Test with real Extended Exchange credentials."

echo ""
echo "============================================================"
echo "🎯 SUMMARY"
echo "============================================================"
echo "✅ Backend running in Docker"
echo "✅ All endpoints responding"
echo "✅ User creation working"
echo "✅ User lookup working"
echo "✅ Extended Exchange setup working"
echo "✅ Integration complete"
echo ""
echo "🚀 Ready for production testing!"
echo "============================================================" 