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

-- ============================================
-- FUNCIÓN PARA REGISTRO AUTOMÁTICO
-- ============================================

-- 11. Crear función para registro automático de credenciales
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

-- 12. Trigger para ejecutar cuando se crea un usuario
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user(); 