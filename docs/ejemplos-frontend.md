# 🎮 **Ejemplos Prácticos para Frontend**

> **Código listo para usar en tu frontend gamificado**

---

## 🚀 **Service API TypeScript/JavaScript**

### **Clase Principal del API**

```typescript
// services/AsTradeAPI.ts
export interface User {
  user_id: string;
  email: string;
  created_at: string;
  has_api_credentials: boolean;
}

export interface Market {
  symbol: string;
  display_name: string;
  base_asset: string;
  quote_asset: string;
  status: string;
  tick_size: string;
  step_size: string;
  min_order_size: string;
  max_order_size: string;
  maker_fee: string;
  taker_fee: string;
  funding_interval: number;
  max_leverage: number;
  is_active: boolean;
}

export interface APIResponse<T> {
  status: string;
  timestamp: string;
  data: T;
  pagination?: any;
}

export class AsTradeAPI {
  private baseURL = 'http://localhost:8000/api/v1';

  // 🔧 Configuración
  constructor(baseURL?: string) {
    if (baseURL) this.baseURL = baseURL;
  }

  // 🏥 Health Check
  async getHealth(): Promise<any> {
    const response = await fetch(`${this.baseURL.replace('/api/v1', '')}/health`);
    return response.json();
  }

  // 👤 Gestión de Usuarios
  async createUser(email: string): Promise<APIResponse<{ user_id: string; message: string }>> {
    const response = await fetch(`${this.baseURL}/users/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getUser(userId: string): Promise<APIResponse<User>> {
    const response = await fetch(`${this.baseURL}/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get user: ${response.statusText}`);
    }
    
    return response.json();
  }

  // 📈 Mercados
  async getMarkets(): Promise<APIResponse<Market[]>> {
    const response = await fetch(`${this.baseURL}/markets/`);
    
    if (!response.ok) {
      throw new Error(`Failed to get markets: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getMarketStats(symbol: string): Promise<APIResponse<any>> {
    const response = await fetch(`${this.baseURL}/markets/${symbol}/stats`);
    
    if (!response.ok) {
      throw new Error(`Failed to get market stats: ${response.statusText}`);
    }
    
    return response.json();
  }

  // 📊 Trading (preparado para futuras implementaciones)
  async getAccount(userId: string): Promise<APIResponse<any>> {
    const response = await fetch(`${this.baseURL}/accounts/${userId}`);
    return response.json();
  }

  async createOrder(orderData: any): Promise<APIResponse<any>> {
    const response = await fetch(`${this.baseURL}/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData)
    });
    return response.json();
  }
}

// Instancia global
export const asTradeAPI = new AsTradeAPI();
```

---

## ⚛️ **React Hooks**

### **Hook para Gestión de Usuario**

```typescript
// hooks/useAsTradeUser.ts
import { useState, useEffect } from 'react';
import { asTradeAPI, User } from '../services/AsTradeAPI';

export const useAsTradeUser = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Crear nuevo jugador
  const createPlayer = async (email: string): Promise<string | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await asTradeAPI.createUser(email);
      const userId = response.data.user_id;
      
      // Guardar en localStorage
      localStorage.setItem('astrade_user_id', userId);
      
      // Cargar información completa del usuario
      await loadUser(userId);
      
      return userId;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error creating user');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Cargar información del usuario
  const loadUser = async (userId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await asTradeAPI.getUser(userId);
      setUser(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading user');
    } finally {
      setLoading(false);
    }
  };

  // Cargar usuario desde localStorage al iniciar
  useEffect(() => {
    const savedUserId = localStorage.getItem('astrade_user_id');
    if (savedUserId) {
      loadUser(savedUserId);
    }
  }, []);

  // Logout
  const logout = () => {
    localStorage.removeItem('astrade_user_id');
    setUser(null);
  };

  return {
    user,
    loading,
    error,
    createPlayer,
    loadUser,
    logout,
    isLoggedIn: !!user
  };
};
```

### **Hook para Mercados**

```typescript
// hooks/useAsTradeMarkets.ts
import { useState, useEffect } from 'react';
import { asTradeAPI, Market } from '../services/AsTradeAPI';

export const useAsTradeMarkets = () => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMarkets = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await asTradeAPI.getMarkets();
      setMarkets(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading markets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMarkets();
  }, []);

  return {
    markets,
    loading,
    error,
    refetch: loadMarkets
  };
};
```

---

## 🎮 **Componentes React Ejemplo**

### **Componente de Login/Registro**

```tsx
// components/LoginForm.tsx
import React, { useState } from 'react';
import { useAsTradeUser } from '../hooks/useAsTradeUser';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const { createPlayer, loading, error } = useAsTradeUser();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) return;
    
    setIsRegistering(true);
    
    const userId = await createPlayer(email);
    
    if (userId) {
      // Redirigir al juego
      window.location.href = '/game';
    }
    
    setIsRegistering(false);
  };

  return (
    <div className="login-form">
      <h1>🎮 Únete a AsTrade</h1>
      <p>El juego de trading más adictivo del universo</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email de Jugador:</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="jugador@astrade.com"
            required
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || isRegistering}
          className="btn btn-primary"
        >
          {isRegistering ? 'Creando jugador...' : '🚀 Comenzar a Jugar'}
        </button>
        
        {error && (
          <div className="error">
            ❌ {error}
          </div>
        )}
      </form>
    </div>
  );
};
```

### **Componente de Mercados**

```tsx
// components/MarketsList.tsx
import React from 'react';
import { useAsTradeMarkets } from '../hooks/useAsTradeMarkets';

export const MarketsList: React.FC = () => {
  const { markets, loading, error } = useAsTradeMarkets();

  if (loading) return <div className="loading">🔄 Cargando mercados...</div>;
  if (error) return <div className="error">❌ {error}</div>;

  return (
    <div className="markets-list">
      <h2>💹 Mercados Disponibles</h2>
      
      <div className="markets-grid">
        {markets.map((market) => (
          <div key={market.symbol} className="market-card">
            <div className="market-header">
              <h3>{market.display_name}</h3>
              <span className={`status ${market.status}`}>
                {market.is_active ? '🟢 Activo' : '🔴 Inactivo'}
              </span>
            </div>
            
            <div className="market-details">
              <div className="detail">
                <label>Apalancamiento:</label>
                <span>{market.max_leverage}x</span>
              </div>
              
              <div className="detail">
                <label>Tamaño mínimo:</label>
                <span>{market.min_order_size} {market.base_asset}</span>
              </div>
              
              <div className="detail">
                <label>Fees:</label>
                <span>{(parseFloat(market.maker_fee) * 100).toFixed(2)}% / {(parseFloat(market.taker_fee) * 100).toFixed(2)}%</span>
              </div>
            </div>
            
            <button 
              className="btn btn-trade"
              onClick={() => {/* Abrir modal de trading */}}
            >
              🎯 Tradear {market.base_asset}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### **Componente Dashboard del Jugador**

```tsx
// components/PlayerDashboard.tsx
import React from 'react';
import { useAsTradeUser } from '../hooks/useAsTradeUser';

export const PlayerDashboard: React.FC = () => {
  const { user, logout } = useAsTradeUser();

  if (!user) return <div>❌ No hay usuario logueado</div>;

  return (
    <div className="player-dashboard">
      <div className="player-header">
        <h1>🎮 Bienvenido, Trader</h1>
        <button onClick={logout} className="btn btn-secondary">
          🚪 Salir
        </button>
      </div>
      
      <div className="player-info">
        <div className="info-card">
          <h3>👤 Información del Jugador</h3>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>ID:</strong> {user.user_id}</p>
          <p><strong>Cuenta desde:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
          <p>
            <strong>Estado:</strong> 
            {user.has_api_credentials ? (
              <span className="success">✅ Configurado</span>
            ) : (
              <span className="warning">⚠️ Pendiente</span>
            )}
          </p>
        </div>
        
        <div className="info-card">
          <h3>🏆 Estadísticas</h3>
          <p><strong>Nivel:</strong> 1 (Novato)</p>
          <p><strong>Experiencia:</strong> 0 XP</p>
          <p><strong>Trades totales:</strong> 0</p>
          <p><strong>P&L total:</strong> $0.00</p>
        </div>
      </div>
    </div>
  );
};
```

---

## 🎨 **CSS Básico para Estilo Gamificado**

```css
/* styles/astrade.css */
.login-form {
  max-width: 400px;
  margin: 50px auto;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  color: white;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.markets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.market-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border: 2px solid #f0f0f0;
  transition: all 0.3s ease;
}

.market-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #667eea;
}

.market-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
}

.market-details {
  margin-bottom: 1.5rem;
}

.detail {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.btn-trade {
  width: 100%;
  background: linear-gradient(45deg, #2ed573, #26d1a3);
  color: white;
}

.player-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.player-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.success {
  color: #2ed573;
}

.warning {
  color: #ffa502;
}

.error {
  color: #ff4757;
  background: #ffe8e8;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}
```

---

## 🚀 **Context Provider (React)**

```tsx
// contexts/AsTradeContext.tsx
import React, { createContext, useContext, ReactNode } from 'react';
import { useAsTradeUser } from '../hooks/useAsTradeUser';
import { useAsTradeMarkets } from '../hooks/useAsTradeMarkets';

interface AsTradeContextType {
  user: ReturnType<typeof useAsTradeUser>;
  markets: ReturnType<typeof useAsTradeMarkets>;
}

const AsTradeContext = createContext<AsTradeContextType | null>(null);

export const AsTradeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const user = useAsTradeUser();
  const markets = useAsTradeMarkets();

  return (
    <AsTradeContext.Provider value={{ user, markets }}>
      {children}
    </AsTradeContext.Provider>
  );
};

export const useAsTrade = (): AsTradeContextType => {
  const context = useContext(AsTradeContext);
  if (!context) {
    throw new Error('useAsTrade must be used within AsTradeProvider');
  }
  return context;
};
```

---

## 📱 **App Principal (React)**

```tsx
// App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AsTradeProvider, useAsTrade } from './contexts/AsTradeContext';
import { LoginForm } from './components/LoginForm';
import { PlayerDashboard } from './components/PlayerDashboard';
import { MarketsList } from './components/MarketsList';
import './styles/astrade.css';

const ProtectedRoute: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user } = useAsTrade();
  
  if (!user.isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

const GamePage: React.FC = () => {
  return (
    <div className="game-page">
      <PlayerDashboard />
      <MarketsList />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AsTradeProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route 
              path="/game" 
              element={
                <ProtectedRoute>
                  <GamePage />
                </ProtectedRoute>
              } 
            />
            <Route path="/" element={<Navigate to="/game" replace />} />
          </Routes>
        </div>
      </Router>
    </AsTradeProvider>
  );
};

export default App;
```

---

## 🧪 **Testing de Integración**

```typescript
// tests/api.test.ts
import { asTradeAPI } from '../services/AsTradeAPI';

describe('AsTrade API Integration', () => {
  test('should get health status', async () => {
    const health = await asTradeAPI.getHealth();
    expect(health.status).toBe('healthy');
  });

  test('should create and retrieve user', async () => {
    // Crear usuario
    const createResponse = await asTradeAPI.createUser('test@example.com');
    expect(createResponse.data.user_id).toBeDefined();
    
    // Obtener usuario
    const userId = createResponse.data.user_id;
    const getResponse = await asTradeAPI.getUser(userId);
    expect(getResponse.data.email).toBe('test@example.com');
  });

  test('should get markets', async () => {
    const response = await asTradeAPI.getMarkets();
    expect(response.data.length).toBeGreaterThan(0);
    expect(response.data[0].symbol).toBeDefined();
  });
});
```

---

## 📋 **Checklist de Integración Frontend**

### **Setup Inicial**
- [ ] Instalar dependencias: `react`, `react-router-dom`, `typescript`
- [ ] Copiar el service API (`AsTradeAPI.ts`)
- [ ] Configurar hooks (`useAsTradeUser`, `useAsTradeMarkets`)
- [ ] Configurar context provider (`AsTradeProvider`)

### **Componentes Básicos**
- [ ] Implementar `LoginForm`
- [ ] Implementar `PlayerDashboard`
- [ ] Implementar `MarketsList`
- [ ] Agregar estilos CSS básicos

### **Funcionalidad Core**
- [ ] Crear usuario funciona
- [ ] Login persiste en localStorage
- [ ] Mercados se cargan correctamente
- [ ] Navegación entre páginas

### **Testing**
- [ ] Probar creación de usuario
- [ ] Probar carga de mercados
- [ ] Probar flujo completo login → dashboard
- [ ] Verificar manejo de errores

---

**🎯 Con estos ejemplos, tu equipo de frontend puede empezar a integrar inmediatamente!** 