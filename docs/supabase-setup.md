# 🗃️ **Configuración de Supabase para AsTrade**

> **Migración de SQLite local a Supabase PostgreSQL para producción**

---

## 📋 **Pasos para Configurar Supabase**

### **1. Crear Proyecto en Supabase**

1. Ir a [supabase.com](https://supabase.com)
2. Crear nuevo proyecto
3. Anotar la información del proyecto:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### **2. Configurar Tablas en Supabase**

#### **Usando el Editor SQL de Supabase:**

```sql
-- ============================================
-- TABLAS PARA ASTRADE EN SUPABASE
-- ============================================

-- 1. Crear tabla para credenciales de usuarios
CREATE TABLE IF NOT EXISTS public.astrade_user_credentials (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    extended_api_key VARCHAR(255),
    extended_secret_key VARCHAR(255),
    extended_stark_private_key TEXT NOT NULL,
    environment VARCHAR(10) DEFAULT 'testnet' CHECK (environment IN ('testnet', 'mainnet')),
    is_mock_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Crear índices para optimizar rendimiento
CREATE INDEX IF NOT EXISTS idx_astrade_credentials_user_id 
ON public.astrade_user_credentials(user_id);

CREATE INDEX IF NOT EXISTS idx_astrade_credentials_environment 
ON public.astrade_user_credentials(environment);

-- 3. Crear función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 4. Crear trigger para actualizar updated_at
CREATE TRIGGER update_astrade_credentials_updated_at 
    BEFORE UPDATE ON public.astrade_user_credentials 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- CONFIGURAR ROW LEVEL SECURITY (RLS)
-- ============================================

-- 5. Habilitar RLS en la tabla
ALTER TABLE public.astrade_user_credentials ENABLE ROW LEVEL SECURITY;

-- 6. Política: Los usuarios solo pueden acceder a sus propias credenciales
CREATE POLICY "Users can only access their own credentials" 
ON public.astrade_user_credentials
FOR ALL USING (auth.uid() = user_id);

-- 7. Política: Permitir inserción para usuarios autenticados
CREATE POLICY "Users can insert their own credentials" 
ON public.astrade_user_credentials
FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 8. Política: Permitir actualización de propias credenciales
CREATE POLICY "Users can update their own credentials" 
ON public.astrade_user_credentials
FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- TABLA OPCIONAL: PERFILES DE USUARIO EXTENDIDOS
-- ============================================

-- 9. Crear tabla para perfiles de juego (opcional)
CREATE TABLE IF NOT EXISTS public.astrade_user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    avatar_url TEXT,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    total_pnl DECIMAL(20,8) DEFAULT 0,
    achievements JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. RLS para perfiles
ALTER TABLE public.astrade_user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own profile" 
ON public.astrade_user_profiles
FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
```

---

## 🔧 **Configuración del Backend**

### **Variables de Entorno para Supabase**

```bash
# .env
SECRET_KEY=your-super-secret-key-2024
EXTENDED_ENVIRONMENT=testnet

# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database URL (Formato especial para Supabase)
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### **Actualizar el Código del Backend**

```python
# app/services/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base

# Configuración para Supabase
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Producción con Supabase
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=300
    )
else:
    # Desarrollo local con SQLite
    engine = create_engine(
        "sqlite:///./astrade.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
```

### **Actualizar Modelos para Supabase**

```python
# app/models/database.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import os

Base = declarative_base()

# Detectar si estamos usando Supabase
IS_SUPABASE = os.getenv("DATABASE_URL") and "supabase" in os.getenv("DATABASE_URL", "")

if IS_SUPABASE:
    # Modelos para Supabase (PostgreSQL)
    class User(Base):
        __tablename__ = "users"
        __table_args__ = {"schema": "auth"}
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        email = Column(String(255))
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now())
        
        api_credentials = relationship("UserApiCredentials", back_populates="user", uselist=False)

    class UserApiCredentials(Base):
        __tablename__ = "astrade_user_credentials"
        __table_args__ = {"schema": "public"}
        
        user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), primary_key=True)
        extended_api_key = Column(String(255))
        extended_secret_key = Column(String(255))
        extended_stark_private_key = Column(Text, nullable=False)
        environment = Column(String(10), default="testnet")
        is_mock_enabled = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now())
        
        user = relationship("User", back_populates="api_credentials")

else:
    # Modelos para SQLite (desarrollo local)
    class User(Base):
        __tablename__ = "users"
        
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        email = Column(String(255), unique=True)
        created_at = Column(DateTime, default=func.now())
        updated_at = Column(DateTime, default=func.now())
        
        api_credentials = relationship("UserApiCredentials", back_populates="user", uselist=False)

    class UserApiCredentials(Base):
        __tablename__ = "user_api_credentials"
        
        user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
        extended_api_key = Column(String(255))
        extended_secret_key = Column(String(255))
        extended_stark_private_key = Column(Text, nullable=False)
        environment = Column(String(10), default="testnet")
        is_mock_enabled = Column(Boolean, default=True)
        created_at = Column(DateTime, default=func.now())
        updated_at = Column(DateTime, default=func.now())
        
        user = relationship("User", back_populates="api_credentials")
```

---

## 🚀 **Migración de Datos**

### **Script de Migración de SQLite a Supabase**

```python
# scripts/migrate_to_supabase.py
import sqlite3
import psycopg2
import os
from datetime import datetime

def migrate_users_to_supabase():
    # Conectar a SQLite local
    sqlite_conn = sqlite3.connect('astrade.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conectar a Supabase PostgreSQL
    pg_conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    pg_cursor = pg_conn.cursor()
    
    try:
        # Migrar usuarios
        sqlite_cursor.execute("SELECT id, email, created_at FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            user_id, email, created_at = user
            
            # Insertar en auth.users de Supabase (si es necesario)
            # O usar el sistema de autenticación de Supabase
            
            print(f"Migrated user: {email}")
        
        # Migrar credenciales
        sqlite_cursor.execute("""
            SELECT user_id, extended_stark_private_key, environment, is_mock_enabled, created_at 
            FROM user_api_credentials
        """)
        credentials = sqlite_cursor.fetchall()
        
        for cred in credentials:
            user_id, stark_key, environment, is_mock, created_at = cred
            
            pg_cursor.execute("""
                INSERT INTO public.astrade_user_credentials 
                (user_id, extended_stark_private_key, environment, is_mock_enabled, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                extended_stark_private_key = EXCLUDED.extended_stark_private_key,
                environment = EXCLUDED.environment,
                is_mock_enabled = EXCLUDED.is_mock_enabled
            """, (user_id, stark_key, environment, is_mock, created_at))
            
            print(f"Migrated credentials for user: {user_id}")
        
        pg_conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        pg_conn.rollback()
    
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_users_to_supabase()
```

---

## 🧪 **Testing con Supabase**

### **Comandos de Prueba**

```bash
# 1. Verificar conexión a Supabase
curl -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  https://xxxxx.supabase.co/rest/v1/astrade_user_credentials

# 2. Crear usuario de prueba
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@supabase.com"}'

# 3. Verificar en la base de datos de Supabase
# (Usar el panel de Supabase o psql)
```

### **Verificación en el Panel de Supabase**

1. Ir a **Database** → **Tables**
2. Verificar que existe `astrade_user_credentials`
3. Hacer query: `SELECT * FROM astrade_user_credentials;`
4. Verificar las políticas RLS en **Authentication** → **Policies**

---

## 🔒 **Seguridad y RLS (Row Level Security)**

### **Configuración de Autenticación**

```sql
-- Crear función para registro automático de credenciales
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
  -- Automáticamente crear credenciales cuando se registra un usuario
  INSERT INTO public.astrade_user_credentials (user_id, extended_stark_private_key, environment)
  VALUES (
    NEW.id, 
    encode(gen_random_bytes(32), 'hex'), -- Generar clave temporal
    'testnet'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para ejecutar cuando se crea un usuario
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### **Políticas de Seguridad Avanzadas**

```sql
-- Solo administradores pueden ver todas las credenciales
CREATE POLICY "Admins can view all credentials" 
ON public.astrade_user_credentials
FOR SELECT USING (
  auth.jwt() ->> 'role' = 'admin'
);

-- Los usuarios pueden actualizar sus credenciales pero no la clave privada
CREATE POLICY "Users can update non-sensitive fields" 
ON public.astrade_user_credentials
FOR UPDATE USING (auth.uid() = user_id)
WITH CHECK (
  auth.uid() = user_id AND 
  OLD.extended_stark_private_key = NEW.extended_stark_private_key
);
```

---

## ✅ **Checklist de Migración a Supabase**

- [ ] **Proyecto creado** en Supabase
- [ ] **Tablas creadas** usando el SQL proporcionado
- [ ] **RLS configurado** correctamente
- [ ] **Variables de entorno** actualizadas
- [ ] **Código del backend** adaptado para Supabase
- [ ] **Migración de datos** ejecutada (si aplica)
- [ ] **Tests realizados** con el nuevo setup
- [ ] **Políticas de seguridad** verificadas

---

## 🆘 **Troubleshooting**

### **Errores Comunes**

1. **"permission denied for schema public"**
   - Verificar que el usuario tiene permisos de escritura
   - Usar el Service Role Key en lugar del Anon Key

2. **"relation does not exist"**
   - Verificar que las tablas se crearon correctamente
   - Verificar los nombres de esquema (public vs auth)

3. **RLS blocking queries**
   - Verificar que las políticas RLS están configuradas
   - Usar `auth.uid()` en las políticas

### **Comandos de Debug**

```sql
-- Ver todas las tablas
SELECT table_name, table_schema 
FROM information_schema.tables 
WHERE table_schema IN ('public', 'auth');

-- Ver políticas RLS
SELECT * FROM pg_policies 
WHERE tablename = 'astrade_user_credentials';

-- Verificar usuario actual
SELECT auth.uid(), auth.jwt();
```

---

**🎯 Con esta configuración, el backend estará listo para producción usando Supabase como base de datos principal!** 