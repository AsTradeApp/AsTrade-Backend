-- =====================================================
-- MIGRACIÓN: SISTEMA DE RECOMPENSAS DIARIAS
-- =====================================================

-- Tabla para tracking de recompensas diarias
CREATE TABLE IF NOT EXISTS public.daily_rewards (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    reward_date DATE NOT NULL,
    reward_type VARCHAR(50) NOT NULL, -- 'daily_streak' o 'galaxy_explorer'
    reward_data JSONB NOT NULL, -- {amount: 100, currency: 'credits', item: 'mystery_card'}
    claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    streak_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, reward_date, reward_type)
);

-- Tabla para configuración de recompensas
CREATE TABLE IF NOT EXISTS public.reward_configs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    reward_type VARCHAR(50) NOT NULL,
    day_number INTEGER, -- 1-7 para streak, null para galaxy explorer
    reward_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(reward_type, day_number)
);

-- Tabla para tracking de streaks
CREATE TABLE IF NOT EXISTS public.user_streaks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    streak_type VARCHAR(50) NOT NULL, -- 'daily_login' o 'galaxy_explorer'
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, streak_type)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_daily_rewards_user_date ON public.daily_rewards(user_id, reward_date);
CREATE INDEX IF NOT EXISTS idx_daily_rewards_user_type ON public.daily_rewards(user_id, reward_type);
CREATE INDEX IF NOT EXISTS idx_user_streaks_user_type ON public.user_streaks(user_id, streak_type);

-- Habilitar RLS (Row Level Security)
ALTER TABLE public.daily_rewards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reward_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_streaks ENABLE ROW LEVEL SECURITY;

-- Políticas RLS para daily_rewards
CREATE POLICY "Users can view their own daily rewards" ON public.daily_rewards
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own daily rewards" ON public.daily_rewards
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own daily rewards" ON public.daily_rewards
    FOR UPDATE USING (auth.uid() = user_id);

-- Políticas RLS para reward_configs (lectura pública)
CREATE POLICY "Anyone can view reward configs" ON public.reward_configs
    FOR SELECT USING (true);

-- Políticas RLS para user_streaks
CREATE POLICY "Users can view their own streaks" ON public.user_streaks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own streaks" ON public.user_streaks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own streaks" ON public.user_streaks
    FOR UPDATE USING (auth.uid() = user_id);

-- Insertar configuración de recompensas por defecto
INSERT INTO public.reward_configs (reward_type, day_number, reward_data) VALUES
('daily_streak', 1, '{"amount": 50, "currency": "credits", "type": "credits", "description": "Día 1 - Créditos"}'),
('daily_streak', 2, '{"amount": 75, "currency": "credits", "type": "credits", "description": "Día 2 - Créditos"}'),
('daily_streak', 3, '{"amount": 100, "currency": "credits", "type": "mystery_card", "description": "Día 3 - Carta Misteriosa"}'),
('daily_streak', 4, '{"amount": 125, "currency": "credits", "type": "credits", "description": "Día 4 - Créditos"}'),
('daily_streak', 5, '{"amount": 150, "currency": "credits", "type": "credits", "description": "Día 5 - Créditos"}'),
('daily_streak', 6, '{"amount": 200, "currency": "credits", "type": "credits", "description": "Día 6 - Créditos"}'),
('daily_streak', 7, '{"amount": 500, "currency": "credits", "type": "premium_mystery_variant", "description": "Día 7 - Variante Premium Misteriosa"}'),
('galaxy_explorer', NULL, '{"amount": 25, "currency": "credits", "type": "galaxy_credits", "description": "Explorador de Galaxia"}')
ON CONFLICT (reward_type, day_number) DO NOTHING;

-- Función para inicializar streaks de usuario
CREATE OR REPLACE FUNCTION initialize_user_streaks(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    -- Insertar streaks si no existen
    INSERT INTO public.user_streaks (user_id, streak_type, current_streak, longest_streak)
    VALUES 
        (user_uuid, 'daily_login', 0, 0),
        (user_uuid, 'galaxy_explorer', 0, 0)
    ON CONFLICT (user_id, streak_type) DO NOTHING;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener estado de recompensas diarias
CREATE OR REPLACE FUNCTION get_daily_rewards_status(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
    today_date DATE := CURRENT_DATE;
    daily_streak RECORD;
    galaxy_streak RECORD;
    claimed_today BOOLEAN;
    week_rewards JSON;
BEGIN
    -- Obtener streaks del usuario
    SELECT * INTO daily_streak FROM public.user_streaks 
    WHERE user_id = user_uuid AND streak_type = 'daily_login';
    
    SELECT * INTO galaxy_streak FROM public.user_streaks 
    WHERE user_id = user_uuid AND streak_type = 'galaxy_explorer';
    
    -- Verificar si ya reclamó hoy
    SELECT EXISTS(
        SELECT 1 FROM public.daily_rewards 
        WHERE user_id = user_uuid AND reward_date = today_date
    ) INTO claimed_today;
    
    -- Construir respuesta
    result := json_build_object(
        'can_claim', NOT claimed_today,
        'current_streak', COALESCE(daily_streak.current_streak, 0),
        'longest_streak', COALESCE(daily_streak.longest_streak, 0),
        'galaxy_explorer_days', COALESCE(galaxy_streak.current_streak, 0),
        'claimed_today', claimed_today
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 