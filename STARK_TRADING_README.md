# Stark Trading API

This documentation describes the Stark perpetual trading functionality integrated into the AsTrade backend.

## Overview

The Stark trading API allows you to place and manage orders on Stark perpetual markets directly from your AsTrade backend. This integration wraps the Stark simple trading client and provides RESTful endpoints for order management.

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Stark Trading Client Configuration
STARK_API_KEY=your-stark-api-key-here
STARK_PUBLIC_KEY=your-stark-public-key-here
STARK_PRIVATE_KEY=your-stark-private-key-here
STARK_VAULT=your-stark-vault-id
```

For testing purposes, you can use the example values from `extended.env.example`, but **never use these in production**.

## API Endpoints

All Stark trading endpoints are available under the `/api/v1/stark` prefix.

### 1. Create Order

**POST** `/api/v1/stark/orders`

Create a new Stark perpetual trading order.

#### Request Body

```json
{
  "amount_of_synthetic": "0.0001",
  "price": "100000.1",
  "market_name": "BTC-USD",
  "side": "BUY",
  "post_only": false
}
```

#### Parameters

- `amount_of_synthetic` (decimal): Amount of synthetic asset to trade (must be > 0)
- `price` (decimal): Order price (must be > 0)
- `market_name` (string): Market symbol (e.g., "BTC-USD")
- `side` (enum): Order side - either "BUY" or "SELL"
- `post_only` (boolean): Whether this is a post-only order (default: false)

#### Response

```json
{
  "success": true,
  "data": {
    "external_id": "order_12345",
    "market_name": "BTC-USD",
    "side": "BUY",
    "amount": "0.0001",
    "price": "100000.1",
    "post_only": false,
    "status": "placed",
    "order_data": { ... }
  }
}
```

### 2. Cancel Order (DELETE)

**DELETE** `/api/v1/stark/orders/{order_external_id}`

Cancel an existing Stark order by its external ID.

#### Path Parameters

- `order_external_id` (string): The external ID of the order to cancel

#### Response

```json
{
  "success": true,
  "data": {
    "external_id": "order_12345",
    "status": "cancelled",
    "result": { ... }
  }
}
```

### 3. Cancel Order (POST)

**POST** `/api/v1/stark/orders/cancel`

Alternative endpoint for cancelling orders using POST method.

#### Request Body

```json
{
  "order_external_id": "order_12345"
}
```

### 4. Get Account Information

**GET** `/api/v1/stark/account`

Get Stark account information and status.

#### Response

```json
{
  "success": true,
  "data": {
    "vault": 500029,
    "public_key": "0x24e50fe6d5247d20fedc23889c012c556eee175a398c355903b742b9c545f7f",
    "api_key": "d6062722...",
    "initialized": true
  }
}
```

### 5. Initialize Client

**POST** `/api/v1/stark/client/initialize`

Initialize the Stark trading client manually.

#### Response

```json
{
  "success": true,
  "data": {
    "status": "initialized",
    "message": "Stark trading client initialized successfully",
    "client_initialized": true
  }
}
```

### 6. Health Check

**GET** `/api/v1/stark/health`

Health check endpoint for Stark trading functionality.

#### Response

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "stark_trading",
    "account_configured": true,
    "client_initialized": true
  }
}
```

## Usage Examples

### Using curl

#### Create a buy order:

```bash
curl -X POST "http://localhost:8000/api/v1/stark/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_of_synthetic": "0.0001",
    "price": "100000.1",
    "market_name": "BTC-USD",
    "side": "BUY",
    "post_only": false
  }'
```

#### Cancel an order:

```bash
curl -X DELETE "http://localhost:8000/api/v1/stark/orders/order_12345"
```

#### Check account info:

```bash
curl -X GET "http://localhost:8000/api/v1/stark/account"
```

### Using Python requests

```python
import requests

# Create order
order_data = {
    "amount_of_synthetic": "0.0001",
    "price": "100000.1",
    "market_name": "BTC-USD",
    "side": "BUY",
    "post_only": False
}

response = requests.post(
    "http://localhost:8000/api/v1/stark/orders",
    json=order_data
)

if response.status_code == 200:
    order_result = response.json()
    order_id = order_result["data"]["external_id"]
    print(f"Order created: {order_id}")
    
    # Cancel the order
    cancel_response = requests.delete(
        f"http://localhost:8000/api/v1/stark/orders/{order_id}"
    )
    print(f"Order cancelled: {cancel_response.json()}")
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (validation error, trading error)
- `500`: Internal Server Error

Error responses include detailed error messages:

```json
{
  "detail": "Trading error: Failed to create order: Invalid market symbol"
}
```

## Security Notes

1. **Never commit your actual API keys** to version control
2. Use environment variables for all sensitive configuration
3. The API keys and private keys in the example are for testing only
4. Consider implementing additional authentication/authorization for production use

## Testing

You can test the integration using the provided example credentials in testnet mode. The health check endpoint is a good starting point to verify the service is working correctly.

## Integration with Frontend

These endpoints can be easily integrated into your frontend application. The API follows RESTful conventions and returns consistent JSON responses that can be easily consumed by web or mobile applications. 