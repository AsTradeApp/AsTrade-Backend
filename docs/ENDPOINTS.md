# 📡 **ENDPOINTS AS TRADE - GUÍA COMPLETA**

> **Base URL**: `http://localhost:8000/api/v1`

---

## 🚀 **CÓMO EJECUTAR**

```bash
# Iniciar el backend
docker-compose up -d

# Verificar que funciona
curl http://localhost:8000/health
```

---

## 📋 **TABLA COMPLETA DE ENDPOINTS**

### **🏥 HEALTH CHECK**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/health` | GET | Ninguno | `{"status": "healthy", "database": {"connected": true}}` |

---

### **👤 USUARIOS**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/users/` | POST | `{"provider": "google", "email": "user@example.com", "cavos_user_id": "google-123", "wallet_address": "0x1234..."}` | `{"success": true, "data": {"user_id": "uuid", "created_at": "timestamp"}}` |
| `/api/v1/users/register` | POST | `{"provider": "google", "email": "user@example.com", "cavos_user_id": "google-123", "wallet_address": "0x1234..."}` | `{"success": true, "data": {"user_id": "uuid", "created_at": "timestamp"}}` |
| `/api/v1/users/{user_id}` | GET | `user_id` en URL | `{"status": "ok", "data": {"user_id": "uuid", "email": "email", "provider": "google", "wallet_address": "0x1234...", "created_at": "timestamp", "has_api_credentials": true, "extended_setup": {...}}}` |
| `/api/v1/users/cavos/{cavos_user_id}` | GET | `cavos_user_id` en URL | Mismo formato que GET user_id |
| `/api/v1/users/{user_id}/extended/setup` | POST | `user_id` en URL | `{"status": "ok", "data": {"setup_completed": true, "message": "Extended Exchange account created successfully", "next_steps": [...]}}` |
| `/api/v1/users/{user_id}/extended/status` | GET | `user_id` en URL | `{"status": "ok", "data": {"user_id": "uuid", "extended_configured": true, "status_message": "Extended Exchange setup verified", "connection_verified": true, "environment": "testnet", "features": {...}}}` |
| `/api/v1/users/integration/status` | GET | Ninguno | `{"status": "ok", "data": {"database": {...}, "endpoints": {...}, "features": {...}}}` |
| `/api/v1/users/{user_id}/extended/onboard-starknet` | POST | `user_id` en URL + `{"address": "0x1234...", "network": "sepolia", "public_key": "0x5678...", "private_key": "0x9abc...", "user_id": "cavos_id", "org_id": "org_id", "access_token": "token", "referral_code": "code"}` | `{"success": true, "account_id": "extended_account_id", "transaction_hash": "0xhash", "environment": "testnet", "message": "Extended Exchange account created successfully", "setup_completed": true, "next_steps": [...]}` |

---

### **📊 MERCADOS**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/markets/` | GET | Ninguno | `{"status": "ok", "data": [{"symbol": "BTC-USD", "lastPrice": 43250, ...}]}` |
| `/api/v1/markets/trending` | GET | `limit` (query param, default 10) | `{"status": "ok", "data": [{"symbol": "BTC-USD", "lastPrice": 43250, "priceChange24h": 1250, "priceChangePercent24h": 2.3, "volume24h": 1250000, ...}]}` |
| `/api/v1/markets/stats` | GET | `symbol` (query param, opcional) | `{"status": "ok", "data": {"symbol": "BTC-USD", "lastPrice": 43250, "priceChange24h": 1250, ...}}` |
| `/api/v1/markets/{symbol}/orderbook` | GET | `symbol` en URL | `{"status": "ok", "data": {"symbol": "BTC-USD", "bids": [...], "asks": [...], "timestamp": "timestamp"}}` |
| `/api/v1/markets/{symbol}/trades` | GET | `symbol` en URL | `{"status": "ok", "data": [{"id": "trade_id", "price": 43250, "size": 0.1, "side": "BUY", "timestamp": "timestamp"}]}` |
| `/api/v1/markets/{symbol}/candles` | GET | `symbol` en URL + `interval` (query param, default "1h") | `{"status": "ok", "data": [{"timestamp": "timestamp", "open": 43200, "high": 43300, "low": 43100, "close": 43250, "volume": 1000}]}` |

---

### **📈 ÓRDENES**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/orders/` | POST | `{"symbol": "BTC-USD", "side": "BUY", "type": "LIMIT", "size": 0.1, "price": 43250, "post_only": true}` | `{"status": "ok", "data": {"order_id": "uuid", "status": "PENDING", "symbol": "BTC-USD", ...}}` |
| `/api/v1/orders/` | GET | `symbol`, `status`, `limit`, `cursor` (query params) | `{"status": "ok", "data": [{"order_id": "uuid", "symbol": "BTC-USD", "side": "BUY", "status": "PENDING", ...}], "pagination": {...}}` |
| `/api/v1/orders/test-extended` | POST | `{"market": "BTC-USD", "amount": 0.001, "side": "BUY", "post_only": true, "auto_cancel": true}` | `{"status": "ok", "data": {"account_info": {...}, "order_result": {...}, "cancellation_result": {...}, "execution_log": [...]}}` |
| `/api/v1/orders/test-extended-demo` | POST | Mismo formato que test-extended | Mismo formato que test-extended (sin autenticación) |

---

### **💰 CUENTAS**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/account/balance` | GET | Header: `X-User-ID: uuid` | `{"status": "ok", "data": {"total_balance": 1000, "available_balance": 950, "reserved_balance": 50, "unrealized_pnl": 25, "user_info": {...}}}` |

---

### **⚡ STARK TRADING**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/stark/orders` | POST | `{"amount_of_synthetic": "0.0001", "price": "100000.1", "market_name": "BTC-USD", "side": "BUY", "post_only": false}` | `{"status": "ok", "data": {"order_id": "uuid", "external_id": "0xhash", "status": "PENDING", ...}}` |
| `/api/v1/stark/orders/{order_external_id}` | DELETE | `order_external_id` en URL | `{"status": "ok", "data": {"cancelled": true, "order_id": "uuid", ...}}` |
| `/api/v1/stark/orders/cancel` | POST | `{"order_external_id": "0xhash"}` | Mismo formato que DELETE |
| `/api/v1/stark/positions` | GET | `market` (query param, opcional) | `{"status": "ok", "data": [{"id": 1, "market": "BTC-USD", "side": "LONG", "leverage": "10", "size": "0.1", "value": "4000", "openPrice": "39000", "markPrice": "40000", "unrealisedPnl": "1000", ...}]}` |
| `/api/v1/stark/orders` | GET | `market`, `type`, `side` (query params, opcionales) | `{"status": "ok", "data": [{"id": 1775511783722512384, "externalId": "0xhash", "market": "ETH-USD", "type": "LIMIT", "side": "BUY", "status": "PARTIALLY_FILLED", "price": "3300", "qty": "0.2", "filledQty": "0.1", ...}]}` |
| `/api/v1/stark/account` | GET | Ninguno | `{"status": "ok", "data": {"vault": "vault_id", "public_key": "0xkey", "initialized": true}}` |
| `/api/v1/stark/client/initialize` | POST | Ninguno | `{"status": "ok", "data": {"initialized": true, "message": "Client initialized successfully"}}` |
| `/api/v1/stark/health` | GET | Ninguno | `{"status": "ok", "data": {"status": "healthy", "service": "stark_trading", "account_configured": true, "client_initialized": true, "price_streaming": true}}` |
| `/api/v1/stark/stream/prices/{symbol}` | WebSocket | `symbol` en URL | Stream de precios en tiempo real usando x10 perpetual orderbook |
| `/api/v1/stark/stream/prices/{symbol}/current` | GET | `symbol` en URL | `{"status": "ok", "data": {"symbol": "BTC-USD", "price": 43250, "best_bid": 43248, "best_ask": 43252, "spread": 4, "timestamp": "timestamp"}}` |
| `/api/v1/stark/stream/start/{symbol}` | POST | `symbol` en URL | `{"status": "ok", "data": {"symbol": "BTC-USD", "streaming": true, "message": "Price streaming started for BTC-USD"}}` |

---

### **🪐 PLANETAS Y QUIZZES**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/planets/` | GET | Header: `X-User-ID: uuid` (opcional) | `{"planets": [{"id": 1, "name": "Tierra", "description": "Planeta natal", "image_url": "url", "difficulty": "FÁCIL", "user_progress": {...}}]}` |
| `/api/v1/planets/{planet_id}` | GET | `planet_id` en URL + Header: `X-User-ID: uuid` (opcional) | `{"planet": {"id": 1, "name": "Tierra", "description": "Planeta natal", "image_url": "url", "difficulty": "FÁCIL", "quizzes": [...], "user_progress": {...}}}` |
| `/api/v1/planets/quiz/{quiz_id}` | GET | `quiz_id` en URL + Header: `X-User-ID: uuid` (opcional) | `{"quiz": {"id": 1, "title": "Quiz de Trading", "description": "Aprende sobre trading", "questions": [{"id": 1, "question": "¿Qué es un stop loss?", "options": [...], "correct_answer": null}], "user_progress": {...}}}` |
| `/api/v1/planets/quiz/{quiz_id}/start` | POST | `quiz_id` en URL + Header: `X-User-ID: uuid` | `{"quiz_session": {"id": "uuid", "quiz_id": 1, "started_at": "timestamp", "questions": [{"id": 1, "question": "¿Qué es un stop loss?", "options": [...], "correct_answer": null}]}}` |
| `/api/v1/planets/quiz/submit` | POST | Header: `X-User-ID: uuid` + `{"quiz_id": 1, "answers": [{"question_id": 1, "selected_option": 2}, {"question_id": 2, "selected_option": 1}]}` | `{"result": {"score": 80, "total_questions": 5, "correct_answers": 4, "time_taken": 120, "questions": [{"id": 1, "question": "¿Qué es un stop loss?", "options": [...], "correct_answer": 2, "user_answer": 2, "is_correct": true}]}}` |
| `/api/v1/planets/progress/overview` | GET | Header: `X-User-ID: uuid` | `{"total_planets": 5, "completed_planets": 2, "total_quizzes": 10, "completed_quizzes": 3, "total_score": 250, "average_score": 83.3, "planets_progress": [...], "quizzes_progress": [...]}` |
| `/api/v1/planets/quiz/{quiz_id}/leaderboard` | GET | `quiz_id` en URL + `limit` (query param, default 10) + Header: `X-User-ID: uuid` (opcional) | `{"status": "ok", "data": [{"user_id": "uuid", "display_name": "Usuario", "score": 100, "completion_percentage": 100, "time_taken": 120, "completed_at": "timestamp"}]}` |
| `/api/v1/planets/admin/seed` | POST | Ninguno | `{"status": "ok", "data": {"message": "Seeding functionality not yet implemented. Use the separate seeding script.", "status": "pending"}}` |

---

### **🎁 RECOMPENSAS**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/rewards/daily-status` | GET | Header: `X-User-ID: uuid` | `{"success": true, "data": {"current_streak": 5, "longest_streak": 7, "galaxy_explorer_days": 3, "can_claim": true, "next_reward_in": "2h 30m"}}` |
| `/api/v1/rewards/claim-daily` | POST | Header: `X-User-ID: uuid` + `{"reward_type": "daily_streak"}` | `{"success": true, "data": {"reward_claimed": true, "streak_incremented": true, "experience_gained": 50, "message": "Reward claimed!", "next_reward_in": "24h"}}` |
| `/api/v1/rewards/record-activity` | POST | Header: `X-User-ID: uuid` | `{"success": true, "message": "Activity recorded"}` |
| `/api/v1/rewards/achievements` | GET | Header: `X-User-ID: uuid` | `{"success": true, "data": [{"id": "weekly_warrior", "name": "Weekly Warrior", "description": "Complete 7 consecutive login days", "unlocked": true, "progress": 7, "required": 7}]}` |
| `/api/v1/rewards/streak-info` | GET | Header: `X-User-ID: uuid` | `{"success": true, "data": {"daily_login_streak": 5, "daily_login_longest": 7, "galaxy_explorer_days": 3, "can_claim_today": true, "next_reward_in": "2h 30m"}}` |
| `/api/v1/rewards/profile` | GET | Header: `X-User-ID: uuid` | `{"success": true, "data": {"user_id": "uuid", "display_name": "Usuario", "level": 5, "experience": 1250, "total_trades": 25, "total_pnl": 150.50, "streaks": {...}, "achievements": [...], "recent_rewards": [...]}}` |
| `/api/v1/rewards/nfts` | GET | Header: `X-User-ID: uuid` + `nft_type`, `rarity` (query params, opcionales) | `{"success": true, "data": [{"id": "uuid", "name": "Daily Card 7", "description": "Reward obtained by completing 7 consecutive days", "image_url": "url", "rarity": "COMMON", "acquired_at": "timestamp"}], "total_count": 5, "filters": {...}}` |
| `/api/v1/rewards/nfts/{nft_id}` | GET | `nft_id` en URL + Header: `X-User-ID: uuid` | `{"success": true, "data": {"id": "uuid", "name": "Daily Card 7", "description": "Reward obtained by completing 7 consecutive days", "image_url": "url", "rarity": "COMMON", "metadata": {...}, "acquired_at": "timestamp"}}` |
| `/api/v1/rewards/nfts/stats` | GET | Header: `X-User-ID: uuid` | `{"success": true, "data": {"total_nfts": 5, "by_type": {"daily_card": 3, "achievement": 2}, "by_rarity": {"COMMON": 4, "RARE": 1}, "recent_nfts": [...]}}` |

---

### **📤 UPLOAD DE IMÁGENES**

| **Endpoint** | **Método** | **Datos de Entrada** | **Datos de Salida** |
|--------------|------------|----------------------|---------------------|
| `/api/v1/rewards/upload-reward-image` | POST | Header: `X-User-ID: uuid` + `file` (multipart/form-data) | `{"success": true, "data": {"url": "https://cloudinary.com/image.jpg", "public_id": "astrade-rewards/reward_uuid_filename", "filename": "reward_uuid_filename"}}` |
| `/api/v1/rewards/upload-reward-image-base64` | POST | Header: `X-User-ID: uuid` + `{"base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...", "filename": "reward.png"}` | Mismo formato que upload-reward-image |

---

## 🔄 **FLUJO TÍPICO DE USUARIO**

### **1. Usuario hace login con Cavos**
```
Frontend → Cavos → Obtiene: email, cavos_user_id, wallet_address
```

### **2. Frontend crea usuario en AsTrade**
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "email": "user@example.com",
    "cavos_user_id": "google-123",
    "wallet_address": "0x1234..."
  }'
```

### **3. Frontend guarda el user_id**
```
Recibe: user_id = "fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

### **4. Frontend puede buscar usuario después**
```bash
# Por user_id
curl "http://localhost:8000/api/v1/users/fb16ec78-ff70-4895-9ace-92a1d8202fdb"

# O por cavos_user_id
curl "http://localhost:8000/api/v1/users/cavos/google-123"
```

### **5. Usuario explora mercados**
```bash
# Ver todos los mercados
curl "http://localhost:8000/api/v1/markets/"

# Ver mercados trending
curl "http://localhost:8000/api/v1/markets/trending?limit=5"

# Ver orderbook de BTC-USD
curl "http://localhost:8000/api/v1/markets/BTC-USD/orderbook"
```

### **6. Usuario hace trading**
```bash
# Crear orden (requiere autenticación)
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USD",
    "side": "BUY",
    "type": "LIMIT",
    "size": 0.001,
    "price": 43250,
    "post_only": true
  }'
```

### **7. Usuario reclama recompensas**
```bash
# Ver estado de recompensas
curl "http://localhost:8000/api/v1/rewards/daily-status" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"

# Reclamar recompensa diaria
curl -X POST "http://localhost:8000/api/v1/rewards/claim-daily" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb" \
  -H "Content-Type: application/json" \
  -d '{"reward_type": "daily_streak"}'
```

### **8. Usuario explora planetas**
```bash
# Ver todos los planetas
curl "http://localhost:8000/api/v1/planets/" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"

# Ver detalle de planeta
curl "http://localhost:8000/api/v1/planets/1" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"

# Iniciar quiz
curl -X POST "http://localhost:8000/api/v1/planets/quiz/1/start" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

---

## ❓ **PREGUNTAS FRECUENTES**

**¿Necesito autenticación?**
- La mayoría de endpoints requieren `X-User-ID` header
- Algunos endpoints son públicos (health, markets básicos)

**¿Qué pasa si el usuario ya existe?**
- Se actualiza la información existente
- No se crea duplicado

**¿Extended Exchange funciona?**
- Sí, pero necesita credenciales reales para trading
- Por ahora usa datos simulados (mock)

**¿Puedo hacer trading?**
- Sí, con Stark trading (endpoints `/api/v1/stark/*`)
- Extended Exchange requiere configuración adicional

---

## ⚠️ **ENDPOINTS CON PROBLEMAS DE ROUTING**

> **Nota**: Estos endpoints están definidos en el código pero no funcionan debido a problemas de estructura de rutas en FastAPI.

| **Endpoint** | **Método** | **Problema** | **Causa** |
|--------------|------------|--------------|-----------|
| `/api/v1/planets/health` | GET | ❌ No funciona | Definido después de `/{planet_id}`, FastAPI interpreta "health" como planet_id |
| `/api/v1/rewards/nfts/stats` | GET | ❌ No funciona | Definido después de `/nfts/{nft_id}`, FastAPI interpreta "stats" como nft_id |

### 🔧 **Solución recomendada:**

Para que estos endpoints funcionen, deben moverse **antes** de las rutas con parámetros en sus respectivos archivos:

```python
# En app/api/v1/planets/routes.py
@router.get("/health")  # ← Mover ANTES de @router.get("/{planet_id}")
async def planets_health_check():
    # ...

@router.get("/{planet_id}")  # ← Esta ruta debe ir DESPUÉS
async def get_planet_detail():
    # ...

# En app/api/v1/rewards/routes.py  
@router.get("/nfts/stats")  # ← Mover ANTES de @router.get("/nfts/{nft_id}")
async def get_nft_stats():
    # ...

@router.get("/nfts/{nft_id}")  # ← Esta ruta debe ir DESPUÉS
async def get_nft_detail():
    # ...
```

---

**¡Eso es todo! Los endpoints están organizados por categoría y son simples de usar.** 🎯 