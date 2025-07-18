# Product Requirements Document (PRD) - AsTrade Backend

## 1. Resumen Ejecutivo

**Proyecto**: AsTrade Backend  
**Versión**: 1.0.0  
**Fecha**: Enero 2025  
**Objetivo**: Desarrollo de un backend robusto en Python que integre la API de Extended Exchange para proporcionar servicios de trading de perpetuos a usuarios finales.

## 2. Visión del Producto

AsTrade será una plataforma de trading backend que aprovecha la infraestructura de Extended Exchange (híbrida CLOB + StarkEx L2) para ofrecer:
- Trading de perpetuos descentralizado
- Gestión avanzada de órdenes y posiciones
- Streams de datos en tiempo real
- Gestión segura de fondos con auto-custodia

## 3. Objetivos del Proyecto

### 3.1 Objetivos Primarios
- ✅ Integración completa con Extended Exchange API
- ✅ Servidor FastAPI con endpoints RESTful
- ✅ Gestión de autenticación (API Keys + Stark signatures)
- ✅ Funcionalidades de trading core (órdenes, posiciones, balance)
- ✅ Streams WebSocket para datos en tiempo real

### 3.2 Objetivos Secundarios
- 📊 Dashboard de métricas y analytics
- 🔒 Sistema de risk management
- 📈 Algoritmos de trading automatizado
- 🔄 Sistema de backup y recuperación

## 4. Alcance Técnico

### 4.1 Funcionalidades Core

#### 4.1.1 Gestión de Mercados
- **GET /markets**: Lista de todos los mercados disponibles
- **GET /markets/{symbol}/stats**: Estadísticas de mercado (24h)
- **GET /markets/{symbol}/orderbook**: Order book en tiempo real
- **GET /markets/{symbol}/trades**: Últimos trades ejecutados
- **GET /markets/{symbol}/candles**: Datos históricos OHLCV
- **GET /markets/{symbol}/funding**: Historia de funding rates

#### 4.1.2 Gestión de Cuentas
- **GET /account/balance**: Balance actual y disponible
- **GET /account/positions**: Posiciones abiertas
- **GET /account/positions/history**: Historia de posiciones
- **GET /account/leverage**: Leverage actual por mercado
- **PATCH /account/leverage**: Actualizar leverage
- **GET /account/fees**: Estructura de fees

#### 4.1.3 Gestión de Órdenes
- **POST /orders**: Crear nueva orden
- **PATCH /orders/{order_id}**: Editar orden existente
- **DELETE /orders/{order_id}**: Cancelar orden específica
- **DELETE /orders**: Cancelación masiva
- **GET /orders**: Órdenes abiertas
- **GET /orders/history**: Historia de órdenes
- **GET /trades**: Historia de trades ejecutados

#### 4.1.4 Transferencias y Retiros
- **POST /transfers**: Transferencias entre cuentas
- **POST /withdrawals**: Solicitar retiro
- **GET /deposits**: Historia de depósitos
- **GET /withdrawals**: Historia de retiros

#### 4.1.5 WebSocket Streams
- **Order Book Stream**: Updates del order book en tiempo real
- **Trades Stream**: Trades ejecutados en tiempo real
- **Account Stream**: Updates de cuenta (balance, posiciones, órdenes)
- **Candles Stream**: Updates de precios OHLCV
- **Funding Stream**: Updates de funding rates

### 4.2 Arquitectura Técnica

#### 4.2.1 Stack Tecnológico
- **Backend Framework**: FastAPI (Python 3.9+)
- **HTTP Client**: httpx (async)
- **WebSocket Client**: websockets
- **Database**: PostgreSQL (para logs y cache)
- **Caching**: Redis
- **Authentication**: JWT + Stark signatures
- **Documentation**: OpenAPI/Swagger
- **Testing**: pytest
- **Deployment**: Docker + docker-compose

#### 4.2.2 Estructura del Proyecto
```
AsTrade-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── extended_config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── markets.py
│   │   │   ├── accounts.py
│   │   │   ├── orders.py
│   │   │   ├── transfers.py
│   │   │   └── websocket.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── extended_client.py
│   │   ├── auth_service.py
│   │   ├── trading_service.py
│   │   └── websocket_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── markets.py
│   │   ├── accounts.py
│   │   ├── orders.py
│   │   └── responses.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── validation.py
│   │   └── helpers.py
│   └── tests/
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 5. Casos de Uso Principales

### 5.1 Trading Básico
1. **Usuario consulta mercados disponibles**
2. **Usuario coloca orden limit/market**
3. **Sistema ejecuta orden y actualiza posición**
4. **Usuario monitorea posición en tiempo real**
5. **Usuario cierra posición**

### 5.2 Trading Avanzado
1. **Usuario configura leverage específico**
2. **Usuario coloca órdenes condicionales (TP/SL)**
3. **Usuario utiliza órdenes TWAP**
4. **Sistema gestiona risk management automático**

### 5.3 Gestión de Fondos
1. **Usuario deposita fondos (USDC)**
2. **Usuario transfiere entre sub-cuentas**
3. **Usuario solicita retiro**
4. **Sistema procesa retiro con validaciones**

## 6. Especificaciones de API

### 6.1 Autenticación
- **API Key**: Header `X-Api-Key`
- **Stark Signature**: Para órdenes y transferencias
- **Rate Limiting**: 1,000 req/min (standard), 60,000 req/5min (market makers)

### 6.2 Formato de Respuestas
```json
{
  "status": "ok" | "error",
  "data": object | array,
  "error": {
    "code": number,
    "message": string
  },
  "pagination": {
    "cursor": number,
    "count": number
  }
}
```

### 6.3 Manejo de Errores
- **400**: Bad Request (parámetros inválidos)
- **401**: Unauthorized (API key inválida)
- **403**: Forbidden (permisos insuficientes)
- **429**: Rate Limit Exceeded
- **500**: Internal Server Error

## 7. Consideraciones de Seguridad

### 7.1 Seguridad de API
- Validación estricta de parámetros de entrada
- Rate limiting por IP y usuario
- Logging completo de transacciones
- Encriptación de datos sensibles

### 7.2 Gestión de Claves
- Almacenamiento seguro de API keys
- Rotación periódica de claves
- Separación entre testnet y mainnet
- Backup seguro de Stark keys

## 8. Configuración de Entornos

### 8.1 Testnet (Sepolia)
- **Base URL**: `https://api.testnet.extended.exchange/api/v1`
- **WebSocket**: `wss://api.testnet.extended.exchange/stream.extended.exchange/v1`
- **Faucet**: $100,000 USDC de prueba diarios

### 8.2 Mainnet (Ethereum)
- **Base URL**: `https://api.extended.exchange/api/v1`
- **WebSocket**: `wss://api.extended.exchange/stream.extended.exchange/v1`
- **Collateral**: USDC real

## 9. Métricas y Monitoreo

### 9.1 KPIs Técnicos
- Latencia de respuesta API (<100ms P95)
- Uptime del servidor (>99.9%)
- Rate de errores (<1%)
- Throughput de órdenes por segundo

### 9.2 KPIs de Negocio
- Volumen de trading procesado
- Número de órdenes ejecutadas
- Usuarios activos
- P&L de usuarios

## 10. Plan de Desarrollo

### 10.1 Sprint 1 (Semana 1-2)
- [x] Setup del proyecto y estructura base
- [x] Configuración de Extended Exchange client
- [x] Endpoints públicos (mercados, stats, orderbook)
- [x] Sistema de autenticación básico

### 10.2 Sprint 2 (Semana 3-4)
- [ ] Endpoints privados (cuenta, balance, posiciones)
- [ ] Sistema de gestión de órdenes
- [ ] Validaciones y manejo de errores
- [ ] Tests unitarios

### 10.3 Sprint 3 (Semana 5-6)
- [ ] WebSocket streams implementation
- [ ] Sistema de transferencias y retiros
- [ ] Dashboard de monitoreo
- [ ] Documentación completa

### 10.4 Sprint 4 (Semana 7-8)
- [ ] Optimizaciones de performance
- [ ] Sistema de logging avanzado
- [ ] Deploy a producción
- [ ] Testing en entorno real

## 11. Riesgos y Mitigaciones

### 11.1 Riesgos Técnicos
- **Latencia de API**: Implementar caching inteligente
- **Rate limiting**: Pool de conexiones y backoff
- **Fallas de red**: Sistema de retry automático
- **Pérdida de datos**: Backup incremental

### 11.2 Riesgos de Seguridad
- **Exposición de claves**: Vault de secretos
- **Ataques DDoS**: WAF y rate limiting
- **Transacciones maliciosas**: Validación múltiple
- **Acceso no autorizado**: Autenticación 2FA

## 12. Criterios de Aceptación

### 12.1 Funcionales
- ✅ Todos los endpoints core implementados
- ✅ WebSocket streams funcionando
- ✅ Sistema de autenticación seguro
- ✅ Manejo robusto de errores
- ✅ Documentación completa de API

### 12.2 No Funcionales
- ✅ Latencia < 100ms para consultas
- ✅ Uptime > 99.9%
- ✅ Cobertura de tests > 90%
- ✅ Documentación actualizada
- ✅ Logs estructurados y monitoreables

---

**Aprobación del PRD**:
- [ ] Product Owner
- [ ] Tech Lead
- [ ] Security Team
- [ ] QA Team

**Fecha de última actualización**: Enero 2025 