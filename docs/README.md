# 🎮 **AsTrade Backend - Documentación Completa**

> **Backend gamificado para trading de futuros perpetuos en StarkNet**  
> Desarrollado para la Hackathon de StarkWare 2024

---

## 📋 **Índice**

1. [🚀 Inicio Rápido](#-inicio-rápido)
2. [🏗️ Arquitectura](#️-arquitectura)
3. [📡 API Endpoints](#-api-endpoints)
4. [🔐 Gestión de Usuarios](#-gestión-de-usuarios)
5. [💹 Mercados y Trading](#-mercados-y-trading)
6. [🗃️ Base de Datos](#️-base-de-datos)
7. [🔧 Configuración para Producción](#-configuración-para-producción)
8. [🎯 Integración con Frontend](#-integración-con-frontend)

---

## 🚀 **Inicio Rápido**

### **Prerrequisitos**
```bash
# Python 3.11+
# Git
# (Opcional) Docker
```

### **Instalación Local**
```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd AsTrade-backend

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install fastapi uvicorn sqlalchemy structlog httpx pydantic-settings

# 4. Ejecutar el backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Verificar Instalación**
```bash
curl http://localhost:8000/health
# ✅ Debería retornar: {"status":"healthy",...}
```

---

## 🏗️ **Arquitectura**

```
AsTrade-backend/
├── app/
│   ├── api/v1/           # Endpoints de la API
│   │   ├── users.py      # Gestión de usuarios
│   │   ├── markets.py    # Mercados y precios
│   │   └── orders.py     # Órdenes de trading
│   ├── models/           # Modelos de datos
│   │   ├── database.py   # Modelos SQLAlchemy
│   │   ├── users.py      # Schemas de usuarios
│   │   └── responses.py  # Schemas de respuestas
│   ├── services/         # Lógica de negocio
│   │   ├── database.py   # Conexión a BD
│   │   └── extended_client.py # Cliente Extended Exchange
│   ├── config/           # Configuración
│   └── main.py           # Aplicación principal
├── docs/                 # Documentación
└── requirements.txt      # Dependencias
```

### **Tecnologías Utilizadas**
- **FastAPI**: Framework web asíncrono
- **SQLAlchemy**: ORM para base de datos
- **SQLite**: Base de datos (desarrollo)
- **Supabase**: Base de datos (producción)
- **Extended Exchange API**: Trading de futuros perpetuos
- **StarkEx**: Claves criptográficas para StarkNet

---

## 📡 **API Endpoints**

### **Base URL**: `http://localhost:8000/api/v1`

### **1. Health Check**
```http
GET /health
```
**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-20T08:51:16.294474",
  "version": "1.0.0",
  "environment": "testnet",
  "uptime": 9.05,
  "services": {
    "extended_exchange": "disconnected",
    "api": "healthy"
  }
}
```

### **2. Usuarios**

#### **Crear Usuario**
```http
POST /api/v1/users/
Content-Type: application/json

{
  "email": "player1@astrade.com"
}
```

**Respuesta:**
```json
{
  "status": "ok",
  "timestamp": "2025-07-20T08:51:24.861947",
  "data": {
    "user_id": "13575e60-3df8-4e2c-8c6b-8ae4ac8b3743",
    "message": "User created successfully"
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
    "user_id": "13575e60-3df8-4e2c-8c6b-8ae4ac8b3743",
    "email": "player1@astrade.com",
    "created_at": "2025-07-20T08:51:24",
    "has_api_credentials": true
  }
}
```

### **3. Mercados**

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
      "display_name": "Bitcoin / USD",
      "base_asset": "BTC",
      "quote_asset": "USD",
      "status": "active",
      "tick_size": "0.1",
      "step_size": "0.001",
      "min_order_size": "0.001",
      "max_order_size": "100.0",
      "maker_fee": "0.0002",
      "taker_fee": "0.0005",
      "funding_interval": 8,
      "max_leverage": 20,
      "is_active": true
    }
  ]
}
```

---

## 🔐 **Gestión de Usuarios**

### **Flujo de Creación de Usuario**

1. **Frontend llama** → `POST /users/`
2. **Backend genera**:
   - UUID único para el usuario
   - Clave StarkEx privada (formato: `0x...`)
   - Credenciales API para Extended Exchange
3. **Backend almacena** en base de datos
4. **Backend retorna** solo el `user_id` (🔒 **nunca la clave privada**)

### **Seguridad de Claves**

```python
# ✅ CORRECTO: La clave se almacena en el backend
user_credentials = {
    "user_id": "abc123...",
    "extended_stark_private_key": "0x724d2fbca6a2ea0c...",  # Solo en BD
    "environment": "testnet",
    "is_mock_enabled": True
}

# ✅ CORRECTO: El frontend solo recibe esto
frontend_response = {
    "user_id": "abc123...",
    "message": "User created successfully"
}
```

### **Casos de Uso para el Videojuego**

```typescript
// 1. Jugador nuevo entra al juego
const newUser = await fetch('/api/v1/users/', {
  method: 'POST',
  body: JSON.stringify({ email: 'player@game.com' })
});

// 2. Obtener información del jugador
const userInfo = await fetch(`/api/v1/users/${userId}`);

// 3. El backend maneja automáticamente las claves StarkEx
// El frontend solo necesita el user_id para todas las operaciones
```

---

## 💹 **Mercados y Trading**

### **Mercados Disponibles**

| **Par** | **Apalancamiento** | **Tamaño Mínimo** | **Tamaño Máximo** | **Fees** |
|---------|-------------------|-------------------|-------------------|----------|
| BTC-USD | 20x              | 0.001 BTC        | 100.0 BTC        | 0.02%/0.05% |
| ETH-USD | 20x              | 0.01 ETH         | 1,000.0 ETH      | 0.02%/0.05% |
| SOL-USD | 15x              | 0.1 SOL          | 10,000.0 SOL     | 0.02%/0.05% |

### **Características del Trading**

- ✅ **Futuros Perpetuos**: Sin fecha de vencimiento
- ✅ **Apalancamiento**: Hasta 20x en BTC y ETH
- ✅ **Funding**: Cada 8 horas
- ✅ **Fees Competitivos**: 0.02% maker / 0.05% taker
- ✅ **Modo Testnet**: Perfecto para el videojuego

---

## 🗃️ **Base de Datos**

### **Esquema Local (SQLite)**

```sql
-- Tabla de usuarios
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,           -- UUID del usuario
    email VARCHAR(255) UNIQUE,            -- Email del jugador
    created_at DATETIME DEFAULT NOW(),    -- Fecha de creación
    updated_at DATETIME DEFAULT NOW()     -- Última actualización
);

-- Tabla de credenciales API
CREATE TABLE user_api_credentials (
    user_id VARCHAR(36) PRIMARY KEY,                    -- FK a users.id
    extended_api_key VARCHAR(255),                      -- API key (opcional)
    extended_secret_key VARCHAR(255),                   -- Secret key (opcional)
    extended_stark_private_key TEXT NOT NULL,           -- 🔑 Clave StarkEx
    environment VARCHAR(10) DEFAULT 'testnet',          -- testnet/mainnet
    is_mock_enabled BOOLEAN DEFAULT true,               -- Modo simulación
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### **Migración a Supabase (Producción)**

```sql
-- Crear tabla en Supabase
CREATE TABLE IF NOT EXISTS public.astrade_user_credentials (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    extended_api_key VARCHAR(255),
    extended_secret_key VARCHAR(255),
    extended_stark_private_key TEXT NOT NULL,
    environment VARCHAR(10) DEFAULT 'testnet',
    is_mock_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Políticas RLS (Row Level Security)
ALTER TABLE public.astrade_user_credentials ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own credentials" 
ON public.astrade_user_credentials
FOR ALL USING (auth.uid() = user_id);
```

---

## 🔧 **Configuración para Producción**

### **Variables de Entorno**

```bash
# .env
SECRET_KEY=your-super-secret-key-2024
EXTENDED_ENVIRONMENT=testnet  # o mainnet
DATABASE_URL=postgresql://user:pass@host:port/db
EXTENDED_API_KEY=your-extended-api-key
EXTENDED_SECRET_KEY=your-extended-secret-key
```

### **Despliegue con Docker**

```dockerfile
# Dockerfile ya incluido en el proyecto
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Ejecutar con Docker
docker build -t astrade-backend .
docker run -p 8000:8000 astrade-backend
```

### **Configuración de Supabase**

```python
# app/services/database.py (producción)
DATABASE_URL = "postgresql://postgres:password@host:5432/postgres"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
```

---

## 🎯 **Integración con Frontend**

### **Flujo Completo de Integración**

```mermaid
graph LR
    A[Frontend Gamificado] --> B[POST /users/]
    B --> C[Backend Genera StarkEx Key]
    C --> D[Almacena en Base de Datos]
    D --> E[Retorna user_id]
    E --> F[Frontend Usa user_id]
    F --> G[Todas las Operaciones de Trading]
```

### **Código de Ejemplo para el Frontend**

```typescript
// services/api.ts
class AsTradgeAPI {
  private baseURL = 'http://localhost:8000/api/v1';

  // Crear nuevo jugador
  async createUser(email: string) {
    const response = await fetch(`${this.baseURL}/users/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return response.json();
  }

  // Obtener información del jugador
  async getUser(userId: string) {
    const response = await fetch(`${this.baseURL}/users/${userId}`);
    return response.json();
  }

  // Obtener mercados disponibles
  async getMarkets() {
    const response = await fetch(`${this.baseURL}/markets/`);
    return response.json();
  }
}

// Uso en React/Vue/Angular
const api = new AsTradeAPI();

// En el componente de login/registro
const handleCreatePlayer = async (email: string) => {
  try {
    const result = await api.createUser(email);
    const userId = result.data.user_id;
    
    // Guardar userId en localStorage/context
    localStorage.setItem('astrade_user_id', userId);
    
    // Redirigir al juego
    router.push('/game');
  } catch (error) {
    console.error('Error creating player:', error);
  }
};
```

### **Estados del Usuario en el Juego**

```typescript
interface GameUser {
  userId: string;              // Del backend
  email: string;              // Del backend
  displayName?: string;       // Frontend only
  level: number;              // Frontend only
  experience: number;         // Frontend only
  achievements: string[];     // Frontend only
  hasApiCredentials: boolean; // Del backend
}
```

### **Endpoints Listos para Usar**

```bash
# 🟢 FUNCIONANDO AHORA
GET  /health                    # Status del sistema
POST /api/v1/users/            # Crear jugador
GET  /api/v1/users/{user_id}   # Info del jugador
GET  /api/v1/markets/          # Mercados disponibles

# 🟡 EN DESARROLLO (LISTO PARA EXPANDIR)
GET  /api/v1/accounts/{user_id}        # Balance del jugador
POST /api/v1/orders/                   # Crear orden de trading
GET  /api/v1/orders/{user_id}          # Órdenes del jugador
GET  /api/v1/markets/{symbol}/stats    # Estadísticas de mercado
```

---

## 🎮 **Para el Equipo de Desarrollo**

### **Próximos Pasos**

1. **Frontend**: Integrar los endpoints ya funcionales
2. **Trading**: Implementar lógica de órdenes usando las claves StarkEx
3. **Gamificación**: Agregar sistema de niveles y logros
4. **Real-time**: WebSockets para precios en tiempo real
5. **Leaderboard**: Rankings de mejores traders

### **Comandos de Desarrollo**

```bash
# Ejecutar backend en desarrollo
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Probar endpoints
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@astrade.com"}'

# Ver base de datos
sqlite3 astrade.db ".tables"
sqlite3 astrade.db "SELECT * FROM users;"
```

### **Testing de la API**

```bash
# Health check
curl http://localhost:8000/health

# Crear usuario
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"developer@astrade.com"}'

# Obtener mercados
curl http://localhost:8000/api/v1/markets/
```

---

## ✅ **Checklist de Integración**

- [x] **Backend funcionando** en puerto 8000
- [x] **Base de datos** creada y funcionando
- [x] **Usuarios** se pueden crear con claves StarkEx
- [x] **Mercados** disponibles (BTC, ETH, SOL)
- [x] **API documentada** y lista para frontend
- [ ] **Frontend conectado** a los endpoints
- [ ] **Trading funcional** con Extended Exchange
- [ ] **Despliegue en producción** con Supabase

---

**🎯 El backend está listo para que el equipo de frontend comience la integración inmediatamente!** 