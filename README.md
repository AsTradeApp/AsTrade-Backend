# AsTrade Backend

## 📋 Descripción

AsTrade Backend es una API profesional desarrollada en Python con FastAPI que integra la plataforma Extended Exchange para proporcionar servicios de trading de perpetuos descentralizados. El sistema aprovecha la infraestructura híbrida CLOB + StarkEx L2 para ofrecer trading de alta performance con auto-custodia.

## 🏗️ Arquitectura

- **Framework**: FastAPI (Python 3.9+)
- **API Exchange**: Extended Exchange (Testnet/Mainnet)
- **HTTP Client**: aiohttp (async)
- **Database**: PostgreSQL + Supabase
- **Cache**: Redis
- **Authentication**: OAuth (Google/Apple) + Extended API Keys
- **Logging**: Structured logging con structlog
- **Deployment**: Docker + docker-compose

## 🚀 Características

### Core Features
- ✅ **Autenticación**: Login con Google/Apple + Cavos Wallet
- ✅ **Extended Exchange**: Integración automática con Extended Exchange
- ✅ **Trading**: Órdenes, posiciones, balances (Testnet/Mainnet)
- ✅ **Gamificación**: Sistema de niveles y logros
- ✅ **Seguridad**: Manejo seguro de claves StarkEx

### Características Técnicas
- 🔒 **Seguridad**: OAuth, API Keys, Stark signatures
- 📊 **Monitoreo**: Health checks, métricas, logging estructurado
- 🌐 **API REST**: Documentación OpenAPI/Swagger automática
- 🐳 **Containerizado**: Docker ready con docker-compose
- ⚡ **Performance**: Cliente HTTP async, connection pooling

## 📦 Base de Datos

### Estructura de Tablas

#### 1. `auth.users` (Supabase)
- Tabla principal de autenticación
- Almacena datos básicos del usuario (email, etc.)
- Referenciada por las demás tablas

#### 2. `user_wallets` (Supabase)
- Dirección de wallet StarkNet
- Red (testnet/mainnet)
- Hash de creación

#### 3. `astrade_user_credentials` (Supabase)
- Claves privadas StarkEx
- API keys de Extended Exchange
- Configuración de entorno

#### 4. `astrade_user_profiles` (Supabase)
- Nombre y nivel del usuario
- Experiencia y estadísticas
- Logros y trades realizados

## 🌐 API Endpoints

### Usuarios y Autenticación

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/users` | POST | Crear usuario (Google/Apple login) |
| `/api/v1/users/{user_id}` | GET | Obtener información de usuario |
| `/api/v1/users/{user_id}/extended/status` | GET | Estado de Extended Exchange |
| `/api/v1/users/{user_id}/extended/setup` | POST | Configurar Extended Exchange |

### Mercados (Públicos)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/markets` | GET | Listar todos los mercados |
| `/api/v1/markets/stats` | GET | Estadísticas de todos los mercados |
| `/api/v1/markets/{symbol}/stats` | GET | Estadísticas de un mercado específico |
| `/api/v1/markets/{symbol}/orderbook` | GET | Order book de un mercado |
| `/api/v1/markets/{symbol}/trades` | GET | Trades recientes |
| `/api/v1/markets/{symbol}/candles` | GET | Datos OHLCV |
| `/api/v1/markets/{symbol}/funding` | GET | Historia de funding rates |
| `/api/v1/markets/trending` | GET | Mercados más activos por volumen |

### Cuentas (Privados)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/account/balance` | GET | Balance de la cuenta |
| `/api/v1/account/positions` | GET | Posiciones abiertas |
| `/api/v1/account/positions/history` | GET | Historia de posiciones |
| `/api/v1/account/leverage` | GET | Configuración de leverage |
| `/api/v1/account/leverage` | PATCH | Actualizar leverage |
| `/api/v1/account/fees` | GET | Estructura de fees |
| `/api/v1/account/summary` | GET | Resumen de cuenta |

### Órdenes (Privados)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/orders` | POST | Crear nueva orden |
| `/api/v1/orders` | GET | Listar órdenes |
| `/api/v1/orders/history` | GET | Historia de órdenes |
| `/api/v1/orders/{order_id}` | PATCH | Editar orden |
| `/api/v1/orders/{order_id}` | DELETE | Cancelar orden |
| `/api/v1/orders` | DELETE | Cancelar todas las órdenes |
| `/api/v1/orders/trades` | GET | Historia de trades |
| `/api/v1/orders/twap` | POST | Crear orden TWAP |

## 📝 Ejemplos de Uso

### 1. Crear Usuario con Google/Apple

\`\`\`bash
curl -X POST "http://localhost:8000/api/v1/users" \\
  -H "Content-Type: application/json" \\
  -d '{
    "provider": "google",
    "email": "user@example.com",
    "cavos_user_id": "google-oauth2|123456789",
    "wallet_address": "0x1234567890abcdef"
  }'
\`\`\`

Respuesta:
\`\`\`json
{
  "success": true,
  "data": {
    "user_id": "uuid-generado",
    "created_at": "2024-01-23T12:34:56Z"
  }
}
\`\`\`

### 2. Verificar Estado Extended

\`\`\`bash
curl "http://localhost:8000/api/v1/users/{user_id}/extended/status" \\
  -H "accept: application/json"
\`\`\`

Respuesta:
\`\`\`json
{
  "success": true,
  "data": {
    "extended_configured": true,
    "status": "active",
    "environment": "testnet",
    "features": {
      "trading": true,
      "balance_check": true,
      "position_management": true
    }
  }
}
\`\`\`

### 3. Obtener Mercados Trending

\`\`\`bash
curl "http://localhost:8000/api/v1/markets/trending?limit=5" \\
  -H "accept: application/json"
\`\`\`

Respuesta:
\`\`\`json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC-USDT",
      "lastPrice": 43250,
      "priceChange24h": 1250,
      "priceChangePercent24h": 2.3,
      "volume24h": 1250000,
      "high24h": 44000,
      "low24h": 42500,
      "openPrice24h": 42800
    },
    // ... más mercados ordenados por volumen
  ],
  "timestamp": 1705123456789
}
\`\`\`

### 4. Obtener Balance (Autenticado)

\`\`\`bash
curl "http://localhost:8000/api/v1/account/balance" \\
  -H "accept: application/json" \\
  -H "X-User-ID: tu-user-id"
\`\`\`

## 🔧 Configuración Extended Exchange

### 1. Obtener API Keys

#### Testnet (Recomendado para desarrollo)
1. Visita [Extended Exchange Testnet](https://testnet.extended.exchange)
2. Crea una cuenta y genera API keys
3. Obtén $100,000 USDC gratis diariamente del faucet

#### Mainnet (Producción)
1. Visita [Extended Exchange](https://extended.exchange)
2. Crea una cuenta y completa KYC
3. Deposita USDC real
4. Genera API keys de producción

### 2. Configurar Variables de Entorno

\`\`\`env
# Extended Exchange API
EXTENDED_ENVIRONMENT=testnet  # o mainnet
EXTENDED_API_KEY=tu-api-key
EXTENDED_SECRET_KEY=tu-secret-key
EXTENDED_MOCK_ENABLED=false  # true para desarrollo sin API keys

# Supabase
SUPABASE_URL=tu-supabase-url
SUPABASE_KEY=tu-supabase-key

# Security
SECRET_KEY=tu-super-secret-key-aqui
\`\`\`

## 🔒 Seguridad

### Autenticación

1. **OAuth (Google/Apple)**
   - Frontend obtiene datos de usuario
   - Backend crea cuenta AsTrade

2. **Extended Exchange**
   - Generación automática de Stark keys
   - Almacenamiento seguro en Supabase
   - API Keys nunca expuestas al frontend

3. **Requests Autenticados**
   - Header `X-User-ID` para identificar usuario
   - Verificación automática de permisos

### Rate Limiting

- **Standard**: 1,000 requests/minuto
- **Market Makers**: 60,000 requests/5 minutos

## 🧪 Testing

\`\`\`bash
# Ejecutar tests
python -m pytest

# Con coverage
python -m pytest --cov=app

# Tests específicos
python -m pytest app/tests/test_users.py
\`\`\`

## 📊 Monitoreo

### Health Check

\`\`\`bash
curl http://localhost:8000/health
\`\`\`

### Logs

\`\`\`bash
# Ver logs en Docker
docker-compose logs -f api

# Ver logs de Extended Exchange
docker-compose logs -f api | grep "Extended"
\`\`\`

## 🚀 Deployment

### Docker (Recomendado)

\`\`\`bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Reiniciar API
docker-compose restart api
\`\`\`

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama feature
3. Commit tus cambios
4. Push a la rama
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT.

## 🆘 Soporte

- **Documentación Extended**: https://docs.extended.exchange
- **Discord Extended**: https://discord.gg/extended
- **Issues**: Crea un issue en este repositorio

---

**AsTrade Backend v1.0.0** - Trading de perpetuos descentralizado con Extended Exchange
