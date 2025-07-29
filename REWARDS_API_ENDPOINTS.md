# 🎁 SISTEMA DE RECOMPENSAS DIARIAS - API ENDPOINTS

## 📋 **RESUMEN DEL SISTEMA**

AsTrade incluye un sistema completo de recompensas diarias estilo Marvel Snap con **integración perfecta** con la tabla `astrade_user_profiles` existente:

1. **🎯 Recompensas Diarias**: Streak de 7 días con recompensas progresivas
2. **🌌 Explorador de Galaxia**: Sistema estilo Duolingo para uso diario de la app
3. **🏆 Logros**: Sistema de logros basado en streaks
4. **📊 Tracking**: Seguimiento completo de actividad y progreso
5. **🔄 Integración**: Aprovecha los campos existentes de `astrade_user_profiles`

---

## 🗄️ **INTEGRACIÓN CON BASE DE DATOS EXISTENTE**

### **Tabla `astrade_user_profiles` (EXISTENTE)**:
- ✅ **`user_id`**: ID del usuario
- ✅ **`level`**: Nivel del usuario (se actualiza con experiencia)
- ✅ **`experience`**: Experiencia total (se suma con recompensas)
- ✅ **`total_trades`**: Total de trades realizados
- ✅ **`total_pnl`**: PnL total
- ✅ **`achievements`**: Logros del usuario (JSONB)

### **Campos Agregados**:
- 🆕 **`streaks`**: Tracking de streaks (JSONB)
- 🆕 **`daily_rewards_claimed`**: Historial de recompensas (JSONB)

### **Estructura de `streaks`**:
```json
{
  "daily_login": {
    "current_streak": 3,
    "longest_streak": 5,
    "last_activity_date": "2025-07-28"
  },
  "galaxy_explorer": {
    "current_streak": 15,
    "longest_streak": 15,
    "last_activity_date": "2025-07-28"
  }
}
```

### **Estructura de `daily_rewards_claimed`**:
```json
[
  {
    "date": "2025-07-28",
    "type": "daily_streak",
    "reward": {
      "amount": 100,
      "currency": "credits",
      "type": "mystery_nft"
    },
    "streak_count": 3,
    "claimed_at": "2025-07-28T23:35:42.393043Z"
  }
]
```

---

## 🚀 **ENDPOINTS DISPONIBLES**

### **1. OBTENER ESTADO DE RECOMPENSAS DIARIAS**
```http
GET /api/v1/rewards/daily-status
```

**Descripción**: Obtiene el estado completo de las recompensas diarias del usuario

**Headers requeridos**:
```
Authorization: Bearer <token>
```

**Respuesta exitosa** (200):
```json
{
  "success": true,
  "data": {
    "can_claim": true,
    "current_streak": 2,
    "longest_streak": 5,
    "next_reward_in": "19h 37m",
    "today_reward": {
      "day": 3,
      "amount": 100,
      "currency": "credits",
      "type": "mystery_nft",
      "description": "Día 3 - NFT Misterioso"
    },
    "week_rewards": [
      {
        "day": 1,
        "reward": {"amount": 50, "currency": "credits", "type": "credits"},
        "is_claimed": true,
        "is_today": false,
        "is_locked": false,
        "amount": 50
      },
      {
        "day": 2,
        "reward": {"amount": 75, "currency": "credits", "type": "credits"},
        "is_claimed": true,
        "is_today": false,
        "is_locked": false,
        "amount": 75
      },
      {
        "day": 3,
        "reward": {"amount": 100, "currency": "credits", "type": "mystery_nft"},
        "is_claimed": false,
        "is_today": true,
        "is_locked": false,
        "amount": 100
      },
      {
        "day": 4,
        "reward": {"amount": 125, "currency": "credits", "type": "credits"},
        "is_claimed": false,
        "is_today": false,
        "is_locked": true,
        "amount": 125
      }
    ],
    "galaxy_explorer_days": 15
  }
}
```

---

### **2. RECLAMAR RECOMPENSA DIARIA**
```http
POST /api/v1/rewards/claim-daily
```

**Descripción**: Reclama la recompensa diaria del usuario y actualiza experiencia/nivel

**Headers requeridos**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body**:
```json
{
  "reward_type": "daily_streak"
}
```

**Tipos de recompensa**:
- `"daily_streak"`: Recompensa por login diario
- `"galaxy_explorer"`: Recompensa por exploración de galaxia

**Respuesta exitosa** (200):
```json
{
  "success": true,
  "data": {
    "success": true,
    "reward_data": {
      "amount": 100,
      "currency": "credits",
      "type": "mystery_nft",
      "description": "Día 3 - NFT Misterioso"
    },
    "new_streak": 3,
    "message": "¡Recompensa reclamada! +100 experiencia (Nivel 2)"
  }
}
```

**Respuesta de error** (400):
```json
{
  "detail": "Ya reclamaste la recompensa de hoy"
}
```

---

### **3. REGISTRAR ACTIVIDAD DE EXPLORACIÓN**
```http
POST /api/v1/rewards/record-activity
```

**Descripción**: Registra actividad de exploración de galaxia (llamado cuando el usuario usa la app)

**Headers requeridos**:
```
Authorization: Bearer <token>
```

**Respuesta exitosa** (200):
```json
{
  "success": true,
  "message": "Actividad registrada"
}
```

**Respuesta si ya registró hoy** (200):
```json
{
  "success": false,
  "message": "Ya registraste actividad hoy"
}
```

---

### **4. OBTENER LOGROS DEL USUARIO**
```http
GET /api/v1/rewards/achievements
```

**Descripción**: Obtiene los logros del usuario relacionados con streaks

**Headers requeridos**:
```
Authorization: Bearer <token>
```

**Respuesta exitosa** (200):
```json
{
  "success": true,
  "data": {
    "achievements": [
      {
        "id": "week_warrior",
        "name": "Guerrero Semanal",
        "description": "Completa 7 días consecutivos de login",
        "unlocked": false,
        "progress": 42
      },
      {
        "id": "galaxy_master",
        "name": "Maestro de la Galaxia",
        "description": "Explora la galaxia por 30 días consecutivos",
        "unlocked": false,
        "progress": 50
      }
    ],
    "daily_streak": {
      "current_streak": 3,
      "longest_streak": 5
    },
    "galaxy_streak": {
      "current_streak": 15,
      "longest_streak": 15
    },
    "level": 2,
    "experience": 1250,
    "total_trades": 45
  }
}
```

---

### **5. OBTENER INFORMACIÓN DE STREAKS**
```http
GET /api/v1/rewards/streak-info
```

**Descripción**: Obtiene información detallada de los streaks del usuario

**Headers requeridos**:
```
Authorization: Bearer <token>
```

**Respuesta exitosa** (200):
```json
{
  "success": true,
  "data": {
    "daily_login_streak": 3,
    "daily_login_longest": 5,
    "galaxy_explorer_days": 15,
    "can_claim_today": true,
    "next_reward_in": "19h 37m"
  }
}
```

---

### **6. OBTENER PERFIL COMPLETO CON RECOMPENSAS** 🆕
```http
GET /api/v1/rewards/profile
```

**Descripción**: Obtiene el perfil completo del usuario con información de recompensas

**Headers requeridos**:
```
Authorization: Bearer <token>
```

**Respuesta exitosa** (200):
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "display_name": "Trader123",
    "avatar_url": "https://...",
    "level": 2,
    "experience": 1250,
    "total_trades": 45,
    "total_pnl": 1250.50,
    "achievements": [
      {
        "id": "week_warrior",
        "name": "Guerrero Semanal",
        "unlocked": false,
        "progress": 42
      }
    ],
    "streaks": {
      "daily_login": {
        "current_streak": 3,
        "longest_streak": 5,
        "last_activity_date": "2025-07-28"
      },
      "galaxy_explorer": {
        "current_streak": 15,
        "longest_streak": 15,
        "last_activity_date": "2025-07-28"
      }
    },
    "recent_rewards": [
      {
        "date": "2025-07-28",
        "type": "daily_streak",
        "reward": {
          "amount": 100,
          "currency": "credits",
          "type": "mystery_nft"
        },
        "streak_count": 3
      }
    ],
    "created_at": "2025-07-20T10:00:00Z",
    "updated_at": "2025-07-28T23:35:42Z"
  }
}
```

---

## 🎮 **CONFIGURACIÓN DE RECOMPENSAS**

### **Recompensas Diarias (7 días)**:
1. **Día 1**: 50 créditos
2. **Día 2**: 75 créditos  
3. **Día 3**: 100 créditos + NFT Misterioso
4. **Día 4**: 125 créditos
5. **Día 5**: 150 créditos
6. **Día 6**: 200 créditos
7. **Día 7**: 500 créditos + Variante Premium Misteriosa

### **Explorador de Galaxia**:
- **Recompensa**: 25 créditos diarios
- **Logro**: 30 días consecutivos

### **Sistema de Niveles**:
- **Fórmula**: `Nivel = (Experiencia / 1000) + 1`
- **Ejemplo**: 1250 experiencia = Nivel 2

---

## 🔧 **IMPLEMENTACIÓN EN EL FRONTEND**

### **1. Mostrar Modal de Recompensas Diarias**
```javascript
// Obtener estado de recompensas
const response = await fetch('/api/v1/rewards/daily-status', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

// Mostrar modal si puede reclamar
if (data.can_claim) {
  showDailyRewardsModal(data);
}
```

### **2. Reclamar Recompensa**
```javascript
// Reclamar recompensa diaria
const response = await fetch('/api/v1/rewards/claim-daily', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ reward_type: 'daily_streak' })
});

const { data } = await response.json();
if (data.success) {
  showRewardClaimed(data.reward_data);
  updateUserExperience(data.reward_data.amount);
  // Verificar si subió de nivel
  if (data.message.includes('Nivel')) {
    showLevelUpNotification();
  }
}
```

### **3. Registrar Actividad de App**
```javascript
// Llamar cuando el usuario abre la app
const response = await fetch('/api/v1/rewards/record-activity', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

const { success } = await response.json();
if (success) {
  // Mostrar notificación de actividad registrada
  showActivityNotification();
}
```

### **4. Mostrar Perfil Completo**
```javascript
// Obtener perfil completo con recompensas
const response = await fetch('/api/v1/rewards/profile', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const { data } = await response.json();
showUserProfile(data);
// data incluye: level, experience, streaks, achievements, recent_rewards
```

---

## 🗄️ **ESTRUCTURA DE BASE DE DATOS**

### **Integración con Tablas Existentes**:
- **`auth.users`**: Usuarios de autenticación
- **`astrade_user_profiles`**: Perfiles con experiencia, nivel, streaks y logros

### **Campos Utilizados**:
- ✅ **`experience`**: Se suma con recompensas
- ✅ **`level`**: Se recalcula automáticamente
- ✅ **`achievements`**: Se actualiza con nuevos logros
- ✅ **`streaks`**: Tracking de streaks (nuevo campo)
- ✅ **`daily_rewards_claimed`**: Historial de recompensas (nuevo campo)

---

## 🚀 **PRÓXIMOS PASOS**

### **1. Ejecutar Migración SQL**
Ve a **Supabase Dashboard** → **SQL Editor** y ejecuta el contenido del archivo `rewards_integration_migration.sql`

### **2. Implementar en el Frontend**
Usa los endpoints documentados:

```javascript
// Ejemplo: Obtener perfil completo
const response = await fetch('/api/v1/rewards/profile', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

// Mostrar información del usuario
showUserProfile({
  level: data.level,
  experience: data.experience,
  streaks: data.streaks,
  achievements: data.achievements
});
```

### **3. Flujo de Implementación**
1. **Al abrir la app**: Llamar `/record-activity`
2. **Mostrar recompensas**: Llamar `/daily-status` 
3. **Reclamar recompensa**: Llamar `/claim-daily`
4. **Mostrar perfil**: Llamar `/profile`
5. **Mostrar logros**: Llamar `/achievements`

---

## ✅ **VENTAJAS DE LA INTEGRACIÓN**

- **🔄 Reutilización**: Aprovecha la tabla existente `astrade_user_profiles`
- **📊 Consistencia**: Todos los datos del usuario en un solo lugar
- **⚡ Performance**: Menos joins y consultas más eficientes
- **🔒 Seguridad**: Políticas RLS existentes se aplican automáticamente
- **📈 Escalabilidad**: Fácil agregar nuevos campos de gamificación

---

## 📝 **NOTAS IMPORTANTES**

- ✅ **Seguridad**: Todas las rutas requieren autenticación
- ✅ **RLS**: Políticas de seguridad configuradas en Supabase
- ✅ **Performance**: Índices optimizados para consultas rápidas
- ✅ **Escalabilidad**: Sistema preparado para futuras expansiones
- ✅ **Integración**: Perfecta integración con estructura existente 