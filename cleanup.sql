-- Migrar datos de extended_credentials a astrade_user_credentials si existen
INSERT INTO public.astrade_user_credentials (
    user_id,
    extended_api_key,
    extended_secret_key,
    extended_stark_private_key,
    environment,
    is_mock_enabled,
    created_at,
    updated_at
)
SELECT 
    user_id,
    extended_api_key,
    extended_secret_key,
    extended_stark_private_key,
    environment,
    is_mock_enabled,
    created_at,
    updated_at
FROM public.extended_credentials
ON CONFLICT (user_id) 
DO UPDATE SET
    extended_api_key = EXCLUDED.extended_api_key,
    extended_secret_key = EXCLUDED.extended_secret_key,
    extended_stark_private_key = EXCLUDED.extended_stark_private_key,
    environment = EXCLUDED.environment,
    is_mock_enabled = EXCLUDED.is_mock_enabled,
    updated_at = NOW();

-- Eliminar tabla duplicada
DROP TABLE IF EXISTS public.extended_credentials;

-- Asegurar que los triggers estén correctamente configurados
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Crear función para manejar nuevo usuario
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    wallet_address text;
    stark_private_key text;
BEGIN
    -- Generar wallet address (simulado - en producción esto vendría de Cavos)
    wallet_address := '0x' || encode(gen_random_bytes(20), 'hex');
    
    -- Generar stark private key
    stark_private_key := encode(gen_random_bytes(32), 'hex');
    
    -- Crear wallet
    INSERT INTO public.user_wallets (
        user_id,
        address,
        network,
        transaction_hash
    ) VALUES (
        NEW.id,
        wallet_address,
        'sepolia',
        '0x' || encode(gen_random_bytes(32), 'hex')
    );
    
    -- Crear credenciales
    INSERT INTO public.astrade_user_credentials (
        user_id,
        extended_stark_private_key,
        environment,
        is_mock_enabled
    ) VALUES (
        NEW.id,
        stark_private_key,
        'testnet',
        true
    );
    
    -- Crear perfil
    INSERT INTO public.astrade_user_profiles (
        user_id,
        display_name,
        level,
        experience,
        total_trades,
        total_pnl,
        achievements
    ) VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', 'Player ' || substr(NEW.id::text, 1, 8)),
        1,
        0,
        0,
        0,
        '[]'::jsonb
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recrear trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Verificar que todas las tablas tengan RLS habilitado
ALTER TABLE public.user_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.astrade_user_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.astrade_user_profiles ENABLE ROW LEVEL SECURITY;

-- Políticas de RLS para user_wallets
CREATE POLICY "Users can view own wallet"
    ON public.user_wallets
    FOR SELECT
    USING (auth.uid() = user_id);

-- Políticas de RLS para astrade_user_credentials
CREATE POLICY "Users can view own credentials"
    ON public.astrade_user_credentials
    FOR SELECT
    USING (auth.uid() = user_id);

-- Políticas de RLS para astrade_user_profiles
CREATE POLICY "Users can view and update own profile"
    ON public.astrade_user_profiles
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id); 