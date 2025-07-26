-- Agregar campos faltantes a la tabla astrade_user_profiles
ALTER TABLE public.astrade_user_profiles
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS provider VARCHAR(50),
ADD COLUMN IF NOT EXISTS cavos_user_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS wallet_address VARCHAR(255);

-- Crear índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_astrade_profiles_email 
ON public.astrade_user_profiles(email);

CREATE INDEX IF NOT EXISTS idx_astrade_profiles_cavos_user_id 
ON public.astrade_user_profiles(cavos_user_id);

CREATE INDEX IF NOT EXISTS idx_astrade_profiles_wallet_address 
ON public.astrade_user_profiles(wallet_address);

-- Actualizar política RLS para permitir selects con los nuevos campos
DROP POLICY IF EXISTS "Users can manage their own profile" ON public.astrade_user_profiles;

CREATE POLICY "Users can manage their own profile" 
ON public.astrade_user_profiles
FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id); 