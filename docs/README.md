# 🎮 **AsTrade Backend**

> Backend para trading de futuros perpetuos en StarkNet usando Extended Exchange API

## 🚀 **Inicio Rápido**

### **Con Docker (Recomendado)**
```bash
# 1. Clonar y entrar al proyecto
git clone <repo-url>
cd AsTrade-backend

# 2. Iniciar servicios
docker-compose up -d

# 3. Verificar que está corriendo
curl http://localhost:8000/health

# 4. ver logs
docker-compose logs -f api  

```


### **Local (Desarrollo)**
```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 **API Endpoints**

### **Base URL**: `http://localhost:8000/api/v1`

### **1. Usuarios**

#### **Crear Usuario**
```http
POST /api/v1/users/
Content-Type: application/json

{
  "provider": "google",           // "google" o "apple"
  "email": "user@example.com",    // Email del usuario
  "cavos_user_id": "google-oauth2|123...",  // ID del proveedor
  "wallet_address": "0x..."       // Dirección generada por Cavos
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-generado",
    "created_at": "2025-07-24T..."
  }
}
```

#### **Obtener Usuario**
```http
GET /api/v1/users/{user_id}
```

**Respuesta:**
```json
{
  "status": "ok",
  "data": {
    "user_id": "uuid-generado",
    "email": "user@example.com",
    "provider": "google",
    "wallet_address": "0x...",
    "created_at": "2025-07-24T...",
    "has_api_credentials": true
  }
}
```

### **2. Mercados**

#### **Listar Mercados**
```http
GET /api/v1/markets/
```

**Respuesta:**
```json
{
  "status": "ok",
  "data": [
    {
      "symbol": "BTC-USD",
      "base_asset": "BTC",
      "quote_asset": "USD",
      "status": "active",
      "tick_size": 0.1,
      "step_size": 0.001,
      "min_order_size": 0.001,
      "max_order_size": 100.0,
      "maker_fee": 0.0002,
      "taker_fee": 0.0005,
      "funding_interval": 8,
      "max_leverage": 20,
      "is_active": true
    }
  ]
}
```

#### **Mercados en Tendencia**
```http
GET /api/v1/markets/trending?limit=10
```

**Parámetros:**
- `limit` (opcional): Número de mercados a devolver (1-100, default: 10)

**Respuesta:**
```json
{
  "status": "ok",
  "data": [
    {
      "symbol": "SOL-USD",
      "lastPrice": 100.0,
      "priceChange24h": 5.0,
      "priceChangePercent24h": 5.26,
      "volume24h": 10000.0,
      "high24h": 102.0,
      "low24h": 94.0,
      "openPrice24h": 95.0
    }
  ],
  "timestamp": 1705123456789
}
```

#### **Estadísticas de Mercado**
```http
GET /api/v1/markets/stats?symbol=BTC-USD
```

**Respuesta:**
```json
{
  "status": "ok",
  "data": [
    {
      "symbol": "BTC-USD",
      "price": 50000.0,
      "price_24h": 48000.0,
      "volume_24h": 1000.0,
      "volume_7d": 7000.0,
      "trades_24h": 10000,
      "open_interest": 500.0,
      "funding_rate": 0.0001,
      "next_funding_time": "2025-07-24T..."
    }
  ]
}
```

### **3. Cuentas**

#### **Balance de Cuenta**
```http
GET /api/v1/account/balance
X-User-ID: uuid-del-usuario
```

**Respuesta:**
```json
{
  "status": "ok",
  "data": {
    "total_equity": "100000.0",
    "available_balance": "80000.0",
    "used_margin": "20000.0",
    "unrealized_pnl": "5000.0",
    "realized_pnl": "2000.0",
    "positions_value": "25000.0"
  }
}
```

## 🔐 **Seguridad**

### **Autenticación**
- Todos los endpoints que requieren autenticación usan el header `X-User-ID`
- El `user_id` se obtiene al crear el usuario y debe guardarse en el frontend

### **Claves y Credenciales**
- Las claves StarkEx privadas se generan y almacenan en el backend
- Las credenciales de Extended Exchange se manejan internamente
- El frontend NUNCA recibe ni maneja claves privadas

## 🗃️ **Base de Datos**

### **Desarrollo (Docker)**
- PostgreSQL para almacenar usuarios y credenciales
- Redis para caché y sesiones

### **Producción (Supabase)**
- Las credenciales se almacenan en la tabla `extended_credentials`:
```sql
CREATE TABLE IF NOT EXISTS extended_credentials (
    user_id UUID PRIMARY KEY,
    extended_stark_private_key TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🎯 **Mercados Disponibles**

| Par     | Apalancamiento | Min Order | Max Order | Maker/Taker Fee |
|---------|---------------|-----------|-----------|----------------|
| BTC-USD | 20x           | 0.001 BTC | 100 BTC   | 0.02%/0.05%    |
| ETH-USD | 20x           | 0.01 ETH  | 1000 ETH  | 0.02%/0.05%    |
| SOL-USD | 15x           | 0.1 SOL   | 10000 SOL | 0.02%/0.05%    |

## 🔧 **Variables de Entorno**

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/astrade
REDIS_URL=redis://localhost:6379/0
EXTENDED_MOCK_ENABLED=true  # true para desarrollo
```