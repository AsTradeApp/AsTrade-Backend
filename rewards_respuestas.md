# 🎁 **SISTEMA COMPLETO DE RECOMPENSAS Y NFTs - ENDPOINTS Y RESPUESTAS**

## 🛣️ **ENDPOINTS DISPONIBLES**

### **1. 📊 OBTENER ESTADO DE RECOMPENSAS DIARIAS**
```bash
curl -X GET "http://localhost:8000/api/v1/rewards/daily-status" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

### **2. 🎯 RECLAMAR RECOMPENSA DIARIA**
```bash
curl -X POST "http://localhost:8000/api/v1/rewards/claim-daily" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb" \
  -d '{"reward_type": "daily_streak"}'
```

### **3. 🚀 REGISTRAR ACTIVIDAD DE EXPLORADOR DE GALAXIA**
```bash
curl -X POST "http://localhost:8000/api/v1/rewards/record-activity" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb" \
  -d '{"activity_type": "galaxy_explorer"}'
```

### **4. 🏆 OBTENER LOGROS DEL USUARIO**
```bash
curl -X GET "http://localhost:8000/api/v1/rewards/achievements" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

### **5. 📈 OBTENER INFORMACIÓN DE STREAKS**
```bash
curl -X GET "http://localhost:8000/api/v1/rewards/streak-info" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

### **6. 👤 OBTENER PERFIL COMPLETO CON RECOMPENSAS**
```bash
curl -X GET "http://localhost:8000/api/v1/rewards/profile" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

### **7. 🖼️ OBTENER COLECCIÓN DE NFTs**
```bash
curl -X GET "http://localhost:8000/api/v1/rewards/nfts" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

### **8. 🖼️ OBTENER DETALLE DE NFT ESPECÍFICO**
```bash
curl -X GET "http://localhost:8000/api/v1/rewards/nfts/{nft_id}" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

### **9. 📊 OBTENER ESTADÍSTICAS DE NFTs**
```bash
curl -X GET "http://localhost:8000/api/v1/rewards/nfts/stats" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: fb16ec78-ff70-4895-9ace-92a1d8202fdb"
```

---

## 📋 **RESPUESTAS COMPLETAS DE TODOS LOS ENDPOINTS**

### **📊 1. GET /api/v1/rewards/daily-status**
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "can_claim": false,
    "current_streak": 0,
    "longest_streak": 0,
    "next_reward_in": "1d",
    "today_reward": null,
    "week_rewards": [
      {
        "day": 1,
        "reward": {"day": 1, "amount": 50, "currency": "credits", "type": "credits"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": false,
        "amount": 50
      },
      {
        "day": 2,
        "reward": {"day": 2, "amount": 75, "currency": "credits", "type": "credits", "image_url": "https://example.com/nft-cards/card-2.png"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": true,
        "amount": 75
      },
      {
        "day": 3,
        "reward": {"day": 3, "amount": 100, "currency": "credits", "type": "mystery_nft"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": true,
        "amount": 100
      },
      {
        "day": 4,
        "reward": {"day": 4, "amount": 125, "currency": "credits", "type": "credits", "image_url": "https://example.com/nft-cards/card-4.png"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": true,
        "amount": 125
      },
      {
        "day": 5,
        "reward": {"day": 5, "amount": 150, "currency": "credits", "type": "credits"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": true,
        "amount": 150
      },
      {
        "day": 6,
        "reward": {"day": 6, "amount": 200, "currency": "credits", "type": "credits", "image_url": "https://example.com/nft-cards/card-6.png"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": true,
        "amount": 200
      },
      {
        "day": 7,
        "reward": {"day": 7, "amount": 500, "currency": "credits", "type": "premium_mystery_variant"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": true,
        "amount": 500
      }
    ],
    "galaxy_explorer_days": 1
  }
}
```

### **🎯 2. POST /api/v1/rewards/claim-daily**
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "reward_data": {
      "day": 2,
      "amount": 75,
      "currency": "credits",
      "type": "credits",
      "image_url": "https://example.com/nft-cards/card-2.png"
    },
    "new_streak": 2,
    "message": "Reward claimed! +75 experience (Level 1) + NFT added to your collection"
  }
}
```

### **🚀 3. POST /api/v1/rewards/record-activity**
**Respuesta:**
```json
{
  "success": true,
  "message": "Activity recorded"
}
```

### **🏆 4. GET /api/v1/rewards/achievements**
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "achievements": [
      {
        "id": "week_warrior",
        "name": "Weekly Warrior",
        "description": "Complete 7 consecutive login days",
        "unlocked": false,
        "progress": 14
      },
      {
        "id": "master_of_the_galaxy",
        "name": "Master of the Galaxy",
        "description": "Explore the galaxy for 30 consecutive days",
        "unlocked": false,
        "progress": 3
      }
    ],
    "daily_streak": {
      "current_streak": 1,
      "longest_streak": 1,
      "last_activity_date": "2025-07-29"
    },
    "galaxy_streak": {
      "current_streak": 1,
      "longest_streak": 1,
      "last_activity_date": "2025-07-29"
    },
    "level": 1,
    "experience": 50,
    "total_trades": 0
  }
}
```

### **📈 5. GET /api/v1/rewards/streak-info**
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "daily_login_streak": 1,
    "daily_login_longest": 1,
    "galaxy_explorer_days": 1,
    "can_claim_today": false,
    "next_reward_in": "1d"
  }
}
```

### **👤 6. GET /api/v1/rewards/profile**
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "user_id": "fb16ec78-ff70-4895-9ace-92a1d8202fdb",
    "display_name": null,
    "avatar_url": null,
    "level": 1,
    "experience": 50,
    "total_trades": 0,
    "total_pnl": 0.0,
    "achievements": [...],
    "streaks": {
      "daily_login": {
        "current_streak": 1,
        "longest_streak": 1,
        "last_activity_date": "2025-07-29"
      },
      "galaxy_explorer": {
        "current_streak": 1,
        "longest_streak": 1,
        "last_activity_date": "2025-07-29"
      }
    },
    "recent_rewards": [
      {
        "date": "2025-07-29",
        "type": "galaxy_explorer",
        "reward": {
          "amount": 25,
          "currency": "credits",
          "type": "galaxy_credits",
          "description": "Galaxy Explorer Bonus"
        },
        "streak_count": 1
      },
      {
        "date": "2025-07-29",
        "type": "daily_streak",
        "reward": {
          "day": 2,
          "amount": 75,
          "currency": "credits",
          "type": "credits",
          "image_url": "https://example.com/nft-cards/card-2.png"
        },
        "streak_count": 2
      }
    ],
    "created_at": "2025-07-29T00:41:12.294023+00:00",
    "updated_at": "2025-07-29T02:08:30.347148+00:00"
  }
}
```

### **🖼️ 7. GET /api/v1/rewards/nfts**
**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "fb16ec78-ff70-4895-9ace-92a1d8202fdb",
      "nft_type": "daily_reward",
      "nft_name": "Daily Card 2",
      "nft_description": "Reward obtained by completing 2 consecutive days",
      "image_url": "https://example.com/nft-cards/card-2.png",
      "rarity": "common",
      "acquired_date": "2025-07-29",
      "acquired_from": "daily_reward_day_2",
      "metadata": {
        "day_number": 2,
        "streak_count": 2,
        "reward_type": "daily_streak"
      },
      "created_at": "2025-07-29T02:08:30.347148+00:00",
      "updated_at": "2025-07-29T02:08:30.347148+00:00"
    }
  ],
  "total_count": 1,
  "filters": {
    "nft_type": null,
    "rarity": null
  }
}
```

### **🖼️ 8. GET /api/v1/rewards/nfts/{nft_id}**
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "fb16ec78-ff70-4895-9ace-92a1d8202fdb",
    "nft_type": "daily_reward",
    "nft_name": "Daily Card 2",
    "nft_description": "Reward obtained by completing 2 consecutive days",
    "image_url": "https://example.com/nft-cards/card-2.png",
    "rarity": "common",
    "acquired_date": "2025-07-29",
    "acquired_from": "daily_reward_day_2",
    "metadata": {
      "day_number": 2,
      "streak_count": 2,
      "reward_type": "daily_streak"
    },
    "created_at": "2025-07-29T02:08:30.347148+00:00",
    "updated_at": "2025-07-29T02:08:30.347148+00:00"
  }
}
```

### **📊 9. GET /api/v1/rewards/nfts/stats**
**Respuesta:**
```json
{
  "success": true,
  "data": {
    "total_nfts": 1,
    "by_type": {
      "daily_reward": 1
    },
    "by_rarity": {
      "common": 1
    },
    "recent_acquisitions": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "nft_name": "Daily Card 2",
        "image_url": "https://example.com/nft-cards/card-2.png",
        "rarity": "common",
        "acquired_date": "2025-07-29"
      }
    ]
  }
}
```

---

## 🎁 **SISTEMA DE RECOMPENSAS**

### **📅 RECOMPENSAS DIARIAS (7 DÍAS)**

| **Día** | **Recompensa** | **Cantidad** | **Tipo** | **NFT** | **Descripción** |
|---------|----------------|--------------|----------|---------|-----------------|
| **Día 1** | 50 créditos | 50 | `credits` | ❌ | Día 1 - Créditos |
| **Día 2** | 75 créditos | 75 | `credits` | ✅ | Día 2 - Créditos + NFT |
| **Día 3** | 100 créditos | 100 | `mystery_nft` | ❌ | Día 3 - NFT Misterioso |
| **Día 4** | 125 créditos | 125 | `credits` | ✅ | Día 4 - Créditos + NFT |
| **Día 5** | 150 créditos | 150 | `credits` | ❌ | Día 5 - Créditos |
| **Día 6** | 200 créditos | 200 | `credits` | ✅ | Día 6 - Créditos + NFT |
| **Día 7** | 500 créditos | 500 | `premium_mystery_variant` | ❌ | Día 7 - Variante Premium |

### **🚀 EXPLORADOR DE GALAXIA**
| **Actividad** | **Recompensa** | **Cantidad** | **Tipo** | **Descripción** |
|---------------|----------------|--------------|----------|-----------------|
| **Uso diario de la app** | 25 créditos | 25 | `galaxy_credits` | Explorador de Galaxia |

---

## 🖼️ **SISTEMA DE NFTs**

### **📊 TIPOS DE NFTs**
- **`daily_reward`**: Obtenidos por completar días 2, 4, 6
- **`achievement`**: Obtenidos por completar logros
- **`special`**: NFTs especiales por eventos

### **⭐ RAREZAS**
- **`common`**: Días 2, 4
- **`rare`**: Día 6
- **`epic`**: Logros especiales
- **`legendary`**: Eventos únicos

### **🗃️ ESTRUCTURA DE DATOS**
```sql
CREATE TABLE user_nfts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    nft_type VARCHAR(50), -- 'daily_reward', 'achievement', 'special'
    nft_name VARCHAR(100),
    nft_description TEXT,
    image_url TEXT,
    rarity VARCHAR(20), -- 'common', 'rare', 'epic', 'legendary'
    acquired_date DATE,
    acquired_from VARCHAR(50),
    metadata JSONB, -- Datos adicionales
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

---

## 🎯 **ESTADO ACTUAL DEL USUARIO**

- ✅ **Streak diario**: 1 día
- ✅ **Streak galaxia**: 1 día  
- ✅ **Experiencia**: 50 puntos
- ✅ **Nivel**: 1
- ✅ **Recompensas reclamadas hoy**: 2 (daily_streak + galaxy_explorer)
- ✅ **NFTs in collection**: 1 (Daily Card 2)

---

## 🚀 **EJEMPLO DE USO EN FRONTEND**

```javascript
// 1. Verificar estado de recompensas
const status = await fetch('/api/v1/rewards/daily-status', {
  headers: { 'X-User-ID': userId }
});

// 2. Reclamar recompensa (automáticamente agrega NFT si es día 2, 4, 6)
if (status.data.can_claim) {
  await fetch('/api/v1/rewards/claim-daily', {
    method: 'POST',
    headers: { 'X-User-ID': userId },
    body: JSON.stringify({ reward_type: 'daily_streak' })
  });
}

// 3. Ver colección de NFTs
const nfts = await fetch('/api/v1/rewards/nfts', {
  headers: { 'X-User-ID': userId }
});

// 4. Ver estadísticas de NFTs
const stats = await fetch('/api/v1/rewards/nfts/stats', {
  headers: { 'X-User-ID': userId }
});

// 5. Ver perfil completo
const profile = await fetch('/api/v1/rewards/profile', {
  headers: { 'X-User-ID': userId }
});
```

---

## ✅ **FUNCIONALIDADES IMPLEMENTADAS**

- ✅ **Sistema de recompensas diarias** (7 días)
- ✅ **Sistema de explorador de galaxia** (uso diario)
- ✅ **Sistema de streaks** (login y galaxia)
- ✅ **Sistema de niveles y experiencia**
- ✅ **Sistema de logros**
- ✅ **Sistema de NFTs/colección**
- ✅ **Estadísticas de NFTs**
- ✅ **Integración con perfil de usuario**
- ✅ **Configuraciones desde base de datos**

¡El sistema está completamente funcional! 🚀