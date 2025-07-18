# AsTrade Backend

## 📋 Descripción

AsTrade Backend es una API profesional desarrollada en Python con FastAPI que integra la plataforma Extended Exchange para proporcionar servicios de trading de perpetuos descentralizados. El sistema aprovecha la infraestructura híbrida CLOB + StarkEx L2 para ofrecer trading de alta performance con auto-custodia.

## 🏗️ Arquitectura

- **Framework**: FastAPI (Python 3.9+)
- **API Exchange**: Extended Exchange (Testnet/Mainnet)
- **HTTP Client**: httpx (async)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: API Keys + HMAC Signatures
- **Logging**: Structured logging con structlog
- **Deployment**: Docker + docker-compose

## 🚀 Características

### Core Trading Features
- ✅ **Gestión de Mercados**: Obtener mercados, estadísticas, order book, trades, candles
- ✅ **Gestión de Cuentas**: Balance, posiciones, leverage, fees
- ✅ **Gestión de Órdenes**: Crear, editar, cancelar órdenes (limit, market, stop, TWAP)
- ✅ **Historial**: Trades ejecutados, historial de posiciones y órdenes
- ✅ **Transferencias**: Entre cuentas y retiros

### Características Técnicas
- 🔒 **Seguridad**: Autenticación HMAC, rate limiting, validación de datos
- 📊 **Monitoreo**: Health checks, métricas, logging estructurado
- 🌐 **API REST**: Documentación OpenAPI/Swagger automática
- 🐳 **Containerizado**: Docker ready con docker-compose
- ⚡ **Performance**: Cliente HTTP async, connection pooling

## 📦 Instalación

### Prerequisitos

- Python 3.9+
- Docker y docker-compose (opcional pero recomendado)
- PostgreSQL (si no usas Docker)
- Redis (si no usas Docker)

### 1. Clonar el Repositorio

\`\`\`bash
git clone <repository-url>
cd AsTrade-backend
\`\`\`

### 2. Configuración de Variables de Entorno

\`\`\`bash
cp .env.example .env
\`\`\`

Edita el archivo `.env` con tus configuraciones:

\`\`\`env
# Extended Exchange API
EXTENDED_ENVIRONMENT=testnet  # o mainnet
EXTENDED_API_KEY=tu-api-key
EXTENDED_SECRET_KEY=tu-secret-key
EXTENDED_STARK_PRIVATE_KEY=tu-stark-private-key

# Security
SECRET_KEY=tu-super-secret-key-aqui

# Database & Redis (si usas instalación local)
DATABASE_URL=postgresql://user:password@localhost:5432/astrade
REDIS_URL=redis://localhost:6379/0
\`\`\`

### 3. Instalación con Docker (Recomendado)

\`\`\`bash
# Construir y levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down
\`\`\`

### 4. Instalación Local

\`\`\`bash
# Crear entorno virtual
python -m venv env
source env/bin/activate  # En Windows: env\\Scripts\\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python -m app.main
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

### 2. Configurar Stark Keys

Las Stark keys son necesarias para firmar transacciones en StarkEx L2:

\`\`\`python
# Generar Stark private key (ejemplo)
from starkbank.ecdsa import PrivateKey
stark_private_key = PrivateKey()
print(f"Stark Private Key: {stark_private_key.toString()}")
\`\`\`

## 🌐 API Endpoints

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

### 1. Obtener Mercados Disponibles

\`\`\`bash
curl -X GET "http://localhost:8000/api/v1/markets" \\
  -H "accept: application/json"
\`\`\`

### 2. Crear una Orden Limit

\`\`\`bash
curl -X POST "http://localhost:8000/api/v1/orders" \\
  -H "accept: application/json" \\
  -H "Content-Type: application/json" \\
  -H "X-Api-Key: tu-api-key" \\
  -d '{
    "symbol": "BTC-USD",
    "type": "limit",
    "side": "buy",
    "size": "0.001",
    "price": "45000.00",
    "time_in_force": "gtc"
  }'
\`\`\`

### 3. Obtener Balance de Cuenta

\`\`\`bash
curl -X GET "http://localhost:8000/api/v1/account/balance" \\
  -H "accept: application/json" \\
  -H "X-Api-Key: tu-api-key"
\`\`\`

### 4. Crear Orden TWAP

\`\`\`bash
curl -X POST "http://localhost:8000/api/v1/orders/twap" \\
  -H "accept: application/json" \\
  -H "Content-Type: application/json" \\
  -H "X-Api-Key: tu-api-key" \\
  -d '{
    "symbol": "ETH-USD",
    "type": "twap",
    "side": "buy",
    "size": "1.0",
    "duration": 3600,
    "interval": 60,
    "randomize": true
  }'
\`\`\`

## 🧪 Testing

\`\`\`bash
# Ejecutar tests
python -m pytest

# Con coverage
python -m pytest --cov=app

# Tests específicos
python -m pytest app/tests/test_markets.py
\`\`\`

## 📊 Monitoreo

### Health Check

\`\`\`bash
curl http://localhost:8000/health
\`\`\`

### Documentación API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Logs

Los logs están estructurados en formato JSON para facilitar el análisis:

\`\`\`bash
# Ver logs en Docker
docker-compose logs -f api

# Filtrar logs por nivel
docker-compose logs api | grep "ERROR"
\`\`\`

## 🔒 Seguridad

### API Authentication

La autenticación se realiza mediante:
1. **API Key**: Header \`X-Api-Key\`
2. **HMAC Signature**: Para endpoints privados
3. **Timestamp**: Para prevenir replay attacks

### Rate Limiting

- **Standard**: 1,000 requests/minuto
- **Market Makers**: 60,000 requests/5 minutos

### Stark Signatures

Para órdenes y transferencias se requieren firmas Stark:

\`\`\`python
# Ejemplo de firma Stark
from starkbank.ecdsa import PrivateKey, sign

private_key = PrivateKey.fromString(STARK_PRIVATE_KEY)
message_hash = calculate_message_hash(order_data)
signature = sign(message_hash, private_key)
\`\`\`

## 🚀 Deployment

### Producción con Docker

\`\`\`bash
# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Configurar Nginx como reverse proxy
docker-compose --profile production up -d
\`\`\`

### Variables de Entorno de Producción

\`\`\`env
DEBUG=false
EXTENDED_ENVIRONMENT=mainnet
SECRET_KEY=super-secure-production-key
LOG_LEVEL=WARNING
WORKERS=4
\`\`\`

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama feature (\`git checkout -b feature/nueva-funcionalidad\`)
3. Commit tus cambios (\`git commit -am 'Agregar nueva funcionalidad'\`)
4. Push a la rama (\`git push origin feature/nueva-funcionalidad\`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- **Documentación Extended Exchange**: https://docs.extended.exchange
- **Discord Extended**: https://discord.gg/extended
- **Issues**: Crea un issue en este repositorio

## 🎯 Roadmap

### Sprint 2 (Próximamente)
- [ ] WebSocket streams en tiempo real
- [ ] Sistema de transferencias
- [ ] Dashboard de métricas
- [ ] Tests automatizados

### Sprint 3 
- [ ] Algoritmos de trading automatizado
- [ ] Risk management avanzado
- [ ] Notificaciones push
- [ ] Analytics avanzados

### Sprint 4
- [ ] Multi-usuario y roles
- [ ] API rate limiting por usuario
- [ ] Backup y recuperación
- [ ] Deploy en producción

---

**AsTrade Backend v1.0.0** - Desarrollado con ❤️ usando Extended Exchange API
