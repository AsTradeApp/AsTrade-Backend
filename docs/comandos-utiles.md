# 🛠️ **Comandos Útiles para Desarrollo AsTrade**

> **Comandos copy-paste para desarrollo rápido**

---

## 🚀 **Ejecutar el Backend**

### **Desarrollo Local**
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar backend en modo desarrollo
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# En otra terminal - Verificar que funciona
curl http://localhost:8000/health
```

### **Con Docker (Opcional)**
```bash
# Construir imagen
docker build -t astrade-backend .

# Ejecutar contenedor
docker run -p 8000:8000 astrade-backend

# Verificar
curl http://localhost:8000/health
```

---

## 🧪 **Testing de API con curl**

### **Health Check**
```bash
curl http://localhost:8000/health | jq .
```

### **Crear Usuario**
```bash
# Crear usuario básico
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@astrade.com"}' | jq .

# Crear múltiples usuarios para testing
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "player1@astrade.com"}' | jq .

curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "player2@astrade.com"}' | jq .
```

### **Obtener Usuario**
```bash
# Reemplazar USER_ID con el ID real del usuario
export USER_ID="13575e60-3df8-4e2c-8c6b-8ae4ac8b3743"
curl "http://localhost:8000/api/v1/users/$USER_ID" | jq .
```

### **Obtener Mercados**
```bash
# Todos los mercados
curl "http://localhost:8000/api/v1/markets/" | jq .

# Mercados específicos (futuro)
curl "http://localhost:8000/api/v1/markets/BTC-USD/stats" | jq .
```

---

## 🗃️ **Comandos de Base de Datos**

### **SQLite Local**
```bash
# Conectar a la base de datos
sqlite3 astrade.db

# Ver tablas
.tables

# Ver usuarios
SELECT * FROM users;

# Ver credenciales (sin exponer claves)
SELECT user_id, environment, is_mock_enabled, created_at FROM user_api_credentials;

# Contar usuarios
SELECT COUNT(*) as total_users FROM users;

# Salir
.exit
```

### **Limpiar Base de Datos**
```bash
# Eliminar base de datos local (¡CUIDADO!)
rm astrade.db

# Recrear automáticamente al reiniciar el backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📊 **Monitoring y Logs**

### **Ver Logs del Backend**
```bash
# Logs en tiempo real
tail -f logs/astrade.log

# Si usas Docker
docker logs -f astrade-backend
```

### **Verificar Estado del Sistema**
```bash
# Verificar puertos abiertos
lsof -i :8000

# Verificar procesos Python
ps aux | grep uvicorn

# Monitorear recursos
top -p $(pgrep python)
```

---

## 🔧 **Comandos de Desarrollo**

### **Instalar Dependencias**
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias mínimas
pip install fastapi uvicorn sqlalchemy structlog httpx pydantic-settings

# O instalar todo desde requirements.txt
pip install -r requirements.txt
```

### **Linting y Formato**
```bash
# Si tienes black instalado
black app/

# Si tienes flake8 instalado
flake8 app/

# Verificar tipos con mypy
mypy app/
```

---

## 🧪 **Scripts de Testing Automatizado**

### **Test Script Básico**
```bash
#!/bin/bash
# test-api.sh

echo "🚀 Testing AsTrade Backend API"

# Health check
echo "📊 Health Check:"
curl -s http://localhost:8000/health | jq '.status'

# Crear usuario
echo "👤 Creating test user:"
USER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@automated.com"}')

USER_ID=$(echo $USER_RESPONSE | jq -r '.data.user_id')
echo "Created user: $USER_ID"

# Obtener usuario
echo "🔍 Getting user info:"
curl -s "http://localhost:8000/api/v1/users/$USER_ID" | jq '.data.email'

# Obtener mercados
echo "📈 Getting markets:"
MARKETS=$(curl -s "http://localhost:8000/api/v1/markets/")
MARKET_COUNT=$(echo $MARKETS | jq '.data | length')
echo "Available markets: $MARKET_COUNT"

echo "✅ All tests completed!"
```

### **Ejecutar Test**
```bash
# Dar permisos de ejecución
chmod +x test-api.sh

# Ejecutar
./test-api.sh
```

---

## 🐳 **Docker Commands**

### **Desarrollo con Docker**
```bash
# Construir imagen
docker build -t astrade-backend .

# Ejecutar en modo desarrollo
docker run -p 8000:8000 -v $(pwd):/app astrade-backend

# Ver logs
docker logs astrade-backend

# Entrar al contenedor
docker exec -it astrade-backend bash

# Limpiar contenedores
docker rm $(docker ps -aq --filter "ancestor=astrade-backend")
```

### **Docker Compose (si está configurado)**
```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Bajar servicios
docker-compose down

# Reconstruir
docker-compose build --no-cache
```

---

## 🔄 **Scripts de Desarrollo Rápido**

### **Script de Setup Completo**
```bash
#!/bin/bash
# setup-dev.sh

echo "🎮 Setting up AsTrade Development Environment"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activar entorno
source venv/bin/activate

# Instalar dependencias
echo "⬇️ Installing dependencies..."
pip install fastapi uvicorn sqlalchemy structlog httpx pydantic-settings

# Verificar instalación
echo "✅ Verifying installation..."
python -c "import fastapi, uvicorn, sqlalchemy; print('All dependencies installed!')"

echo "🚀 Ready to start development!"
echo "Run: python -m uvicorn app.main:app --reload"
```

### **Script de Limpieza**
```bash
#!/bin/bash
# clean-dev.sh

echo "🧹 Cleaning development environment"

# Matar procesos uvicorn
pkill -f uvicorn

# Limpiar base de datos
rm -f astrade.db

# Limpiar logs
rm -f logs/*.log

# Limpiar __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "✅ Environment cleaned!"
```

---

## 🌐 **Testing con HTTPie (Alternativa a curl)**

### **Instalar HTTPie**
```bash
pip install httpie
```

### **Comandos HTTPie**
```bash
# Health check
http GET localhost:8000/health

# Crear usuario
http POST localhost:8000/api/v1/users/ email=test@httpie.com

# Obtener usuario
http GET localhost:8000/api/v1/users/USER_ID_HERE

# Obtener mercados
http GET localhost:8000/api/v1/markets/
```

---

## 🚨 **Comandos de Emergencia**

### **Reiniciar Todo**
```bash
# Matar todos los procesos relacionados
pkill -f uvicorn
pkill -f python

# Limpiar y reiniciar
rm astrade.db
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Verificar Dependencias**
```bash
# Ver qué está instalado
pip freeze

# Verificar versiones específicas
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
```

### **Cambiar Puerto si 8000 está ocupado**
```bash
# Usar puerto 8001
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Verificar
curl http://localhost:8001/health
```

---

## 📋 **Checklist de Desarrollo Diario**

```bash
# ✅ Checklist matutino
curl http://localhost:8000/health                    # Backend funcionando
curl http://localhost:8000/api/v1/markets/ | jq     # Mercados cargando
sqlite3 astrade.db "SELECT COUNT(*) FROM users;"    # DB funcionando

# ✅ Checklist antes de commit
./test-api.sh                                       # Tests pasando
black app/                                          # Código formateado
git status                                          # Cambios listos
```

---

**🎯 Con estos comandos puedes desarrollar de forma súper eficiente!** 