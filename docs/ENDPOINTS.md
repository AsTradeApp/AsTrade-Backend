# 📡 **ENDPOINTS AS TRADE - GUÍA SIMPLE**

> **Base URL**: `http://localhost:8000/api/v1`

---

## 🚀 **CÓMO EJECUTAR**

### **Con Docker (Recomendado)**
```bash
# Iniciar el backend
docker-compose up -d

# Verificar que funciona
curl http://localhost:8000/health
```

---

## 📋 **ENDPOINTS PRINCIPALES**

### **1. CREAR USUARIO** 
```http
POST /api/v1/users/register
```

**Datos que envías:**
```json
{
  "provider": "google",           // "google" o "apple"
  "email": "user@example.com",    // Email del usuario
  "cavos_user_id": "google-123",  // ID que te da Cavos
  "wallet_address": "0x1234..."   // Wallet que genera Cavos
}
```

**Datos que recibes:**
```json
{
  "success": true,
  "data": {
    "user_id": "fb16ec78-ff70-4895-9ace-92a1d8202fdb",
    "created_at": "2025-07-27T19:53:35.450355"
  }
}
```

**¿Qué hace?**
- Crea perfil de usuario en AsTrade
- Registra la wallet
- Configura Extended Exchange automáticamente
- Te devuelve el user_id para usar en otros endpoints

---

### **2. BUSCAR USUARIO POR ID**
```http
GET /api/v1/users/{user_id}
```

**Datos que envías:**
- Solo el user_id en la URL

**Datos que recibes:**
```json
{
  "status": "ok",
  "data": {
    "user_id": "fb16ec78-ff70-4895-9ace-92a1d8202fdb",
    "email": "user@example.com",
    "provider": "google",
    "wallet_address": "0x1234...",
    "created_at": "2025-07-27T19:53:35.450355",
    "has_api_credentials": true,
    "extended_setup": {
      "is_configured": false,
      "status": "Extended connection failed",
      "environment": "testnet",
      "trading_enabled": false
    }
  }
}
```

**¿Qué hace?**
- Te da toda la información del usuario
- Te dice si tiene Extended Exchange configurado
- Te dice si puede hacer trading

---

### **3. BUSCAR USUARIO POR CAVOS ID**
```http
GET /api/v1/users/cavos/{cavos_user_id}
```

**Datos que envías:**
- Solo el cavos_user_id en la URL

**Datos que recibes:**
```json
{
  "status": "ok",
  "data": {
    "user_id": "fb16ec78-ff70-4895-9ace-92a1d8202fdb",
    "email": "user@example.com",
    "provider": "google",
    "wallet_address": "0x1234...",
    "created_at": "2025-07-27T19:53:35.450355",
    "has_api_credentials": true,
    "extended_setup": {
      "is_configured": false,
      "status": "Extended connection failed",
      "environment": "testnet",
      "trading_enabled": false
    }
  }
}
```

**¿Qué hace?**
- Busca un usuario usando el ID que te da Cavos
- Te devuelve la misma información que el endpoint anterior

---

### **4. CONFIGURAR EXTENDED EXCHANGE**
```http
POST /api/v1/users/{user_id}/extended/setup
```

**Datos que envías:**
- Solo el user_id en la URL

**Datos que recibes:**
```json
{
  "status": "ok",
  "data": {
    "setup_completed": true,
    "message": "Extended Exchange account created successfully",
    "next_steps": [
      "You can now access Extended Exchange features",
      "Start with testnet trading to practice",
      "Check your balance and positions"
    ]
  }
}
```

**¿Qué hace?**
- Configura Extended Exchange para el usuario
- Genera las credenciales necesarias
- Te dice si funcionó y qué hacer después

---

### **5. VER ESTADO DE EXTENDED**
```http
GET /api/v1/users/{user_id}/extended/status
```

**Datos que envías:**
- Solo el user_id en la URL

**Datos que recibes:**
```json
{
  "status": "ok",
  "data": {
    "user_id": "fb16ec78-ff70-4895-9ace-92a1d8202fdb",
    "extended_configured": true,
    "status_message": "Extended Exchange setup verified",
    "connection_verified": true,
    "environment": "testnet",
    "features": {
      "trading": true,
      "balance_check": true,
      "position_management": true,
      "order_history": true,
      "websocket_streams": true
    },
    "limitations": []
  }
}
```

**¿Qué hace?**
- Te dice si Extended Exchange está funcionando
- Te dice qué funcionalidades están disponibles
- Te dice si hay limitaciones

---

### **6. VER ESTADO COMPLETO DE LA INTEGRACIÓN**
```http
GET /api/v1/users/integration/status
```

**Datos que envías:**
- Nada, solo la petición GET

**Datos que recibes:**
```json
{
  "status": "ok",
  "data": {
    "database": {
      "profiles_count": 1,
      "wallets_count": 1,
      "credentials_count": 1,
      "has_sample_data": true
    },
    "endpoints": {
      "user_creation": "✅ POST /api/v1/users/register",
      "user_lookup": "✅ GET /api/v1/users/{user_id}",
      "cavos_lookup": "✅ GET /api/v1/users/cavos/{cavos_user_id}",
      "extended_setup": "✅ POST /api/v1/users/{user_id}/extended/setup",
      "extended_status": "✅ GET /api/v1/users/{user_id}/extended/status"
    },
    "features": {
      "cavos_integration": "✅ User creation with Cavos data",
      "wallet_registration": "✅ Automatic wallet record creation",
      "extended_setup": "✅ Automatic Extended Exchange setup",
      "profile_creation": "✅ Gamification profile creation",
      "credential_storage": "✅ Secure credential storage"
    }
  }
}
```

**¿Qué hace?**
- Te da un resumen completo de todo el sistema
- Te dice cuántos usuarios hay en la base de datos
- Te dice qué endpoints están funcionando
- Te dice qué funcionalidades están disponibles

---

## 🔄 **FLUJO TÍPICO DE USO**

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

---

## ❓ **PREGUNTAS FRECUENTES**

**¿Necesito autenticación?**
- No por ahora, los endpoints son públicos
- En producción se agregará JWT

**¿Qué pasa si el usuario ya existe?**
- Se actualiza la información existente
- No se crea duplicado

**¿Extended Exchange funciona?**
- Sí, pero necesita credenciales reales para trading
- Por ahora usa datos simulados (mock)

**¿Puedo hacer trading?**
- No todavía, falta conectar con Extended Exchange real
- La estructura está lista, solo faltan las credenciales

---

## 🎁 **ENDPOINTS DE RECOMPENSAS**

### **1. OBTENER ESTADO DE RECOMPENSAS**
```http
GET /api/v1/rewards/daily-status
```

### **2. RECLAMAR RECOMPENSA**
```http
POST /api/v1/rewards/claim-daily
```

### **3. REGISTRAR ACTIVIDAD**
```http
POST /api/v1/rewards/record-activity
```

### **4. OBTENER LOGROS**
```http
GET /api/v1/rewards/achievements
```

### **5. OBTENER INFO DE STREAKS**
```http
GET /api/v1/rewards/streak-info
```

### **6. OBTENER PERFIL COMPLETO**
```http
GET /api/v1/rewards/profile
```

### **7. OBTENER COLECCIÓN DE NFTs**
```http
GET /api/v1/rewards/nfts
```

### **8. OBTENER DETALLE DE NFT**
```http
GET /api/v1/rewards/nfts/{nft_id}
```

### **9. OBTENER ESTADÍSTICAS DE NFTs**
```http
GET /api/v1/rewards/nfts/stats
```

---

## 🚨 **ESTADO ACTUAL**

✅ **Funcionando:**
- Creación de usuarios
- Búsqueda de usuarios
- Configuración de Extended
- Almacenamiento seguro
- Sistema de recompensas diarias

🟡 **Parcial:**
- Conexión real con Extended Exchange
- Trading real

⏳ **Pendiente:**
- Credenciales Extended reales
- Trading funcional
- WebSocket para órdenes

---

**¡Eso es todo! Los endpoints son simples y directos.** 🎯 