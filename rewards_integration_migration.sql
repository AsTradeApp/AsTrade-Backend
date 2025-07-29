-- =====================================================
-- MIGRACIÓN: INTEGRACIÓN DE RECOMPENSAS CON astrade_user_profiles
-- =====================================================

-- Agregar campos de streaks y recompensas a la tabla existente
ALTER TABLE public.astrade_user_profiles 
ADD COLUMN IF NOT EXISTS streaks JSONB DEFAULT '{
    "daily_login": {
        "current_streak": 0,
        "longest_streak": 0,
        "last_activity_date": null
    },
    "galaxy_explorer": {
        "current_streak": 0,
        "longest_streak": 0,
        "last_activity_date": null
    }
}'::jsonb;

ALTER TABLE public.astrade_user_profiles 
ADD COLUMN IF NOT EXISTS daily_rewards_claimed JSONB DEFAULT '[]'::jsonb;

-- Actualizar perfiles existentes para incluir los nuevos campos
UPDATE public.astrade_user_profiles 
SET streaks = '{
    "daily_login": {
        "current_streak": 0,
        "longest_streak": 0,
        "last_activity_date": null
    },
    "galaxy_explorer": {
        "current_streak": 0,
        "longest_streak": 0,
        "last_activity_date": null
    }
}'::jsonb,
daily_rewards_claimed = '[]'::jsonb
WHERE streaks IS NULL OR daily_rewards_claimed IS NULL;

-- Crear índices para optimizar consultas de streaks
CREATE INDEX IF NOT EXISTS idx_user_profiles_streaks ON public.astrade_user_profiles USING GIN (streaks);
CREATE INDEX IF NOT EXISTS idx_user_profiles_rewards ON public.astrade_user_profiles USING GIN (daily_rewards_claimed);

-- Función para calcular nivel basado en experiencia
CREATE OR REPLACE FUNCTION calculate_user_level(exp INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN (exp / 1000) + 1;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Función para agregar experiencia y recalcular nivel
CREATE OR REPLACE FUNCTION add_user_experience(user_uuid UUID, exp_to_add INTEGER)
RETURNS JSON AS $$
DECLARE
    current_exp INTEGER;
    new_exp INTEGER;
    new_level INTEGER;
    result JSON;
BEGIN
    -- Obtener experiencia actual
    SELECT experience INTO current_exp 
    FROM public.astrade_user_profiles 
    WHERE user_id = user_uuid;
    
    -- Calcular nueva experiencia y nivel
    new_exp = COALESCE(current_exp, 0) + exp_to_add;
    new_level = calculate_user_level(new_exp);
    
    -- Actualizar perfil
    UPDATE public.astrade_user_profiles 
    SET experience = new_exp, level = new_level, updated_at = NOW()
    WHERE user_id = user_uuid;
    
    -- Construir respuesta
    result := json_build_object(
        'old_experience', current_exp,
        'new_experience', new_exp,
        'experience_gained', exp_to_add,
        'old_level', calculate_user_level(COALESCE(current_exp, 0)),
        'new_level', new_level,
        'leveled_up', calculate_user_level(COALESCE(current_exp, 0)) < new_level
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para actualizar streaks del usuario
CREATE OR REPLACE FUNCTION update_user_streak(
    user_uuid UUID, 
    streak_type TEXT, 
    new_streak INTEGER, 
    is_consecutive BOOLEAN
)
RETURNS JSON AS $$
DECLARE
    current_streaks JSONB;
    updated_streaks JSONB;
    result JSON;
BEGIN
    -- Obtener streaks actuales
    SELECT streaks INTO current_streaks 
    FROM public.astrade_user_profiles 
    WHERE user_id = user_uuid;
    
    -- Actualizar streak específico
    updated_streaks = current_streaks;
    updated_streaks = jsonb_set(
        updated_streaks, 
        ARRAY[streak_type, 'current_streak'], 
        to_jsonb(new_streak)
    );
    
    -- Actualizar longest streak si es necesario
    IF new_streak > (current_streaks->streak_type->>'longest_streak')::INTEGER THEN
        updated_streaks = jsonb_set(
            updated_streaks, 
            ARRAY[streak_type, 'longest_streak'], 
            to_jsonb(new_streak)
        );
    END IF;
    
    -- Actualizar fecha de última actividad
    updated_streaks = jsonb_set(
        updated_streaks, 
        ARRAY[streak_type, 'last_activity_date'], 
        to_jsonb(CURRENT_DATE::TEXT)
    );
    
    -- Guardar en la base de datos
    UPDATE public.astrade_user_profiles 
    SET streaks = updated_streaks, updated_at = NOW()
    WHERE user_id = user_uuid;
    
    -- Construir respuesta
    result := json_build_object(
        'streak_type', streak_type,
        'old_streak', (current_streaks->streak_type->>'current_streak')::INTEGER,
        'new_streak', new_streak,
        'longest_streak', (updated_streaks->streak_type->>'longest_streak')::INTEGER,
        'is_consecutive', is_consecutive
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para registrar recompensa reclamada
CREATE OR REPLACE FUNCTION record_daily_reward(
    user_uuid UUID,
    reward_type TEXT,
    reward_data JSONB,
    streak_count INTEGER
)
RETURNS JSON AS $$
DECLARE
    current_rewards JSONB;
    new_reward JSONB;
    result JSON;
BEGIN
    -- Obtener recompensas actuales
    SELECT daily_rewards_claimed INTO current_rewards 
    FROM public.astrade_user_profiles 
    WHERE user_id = user_uuid;
    
    -- Crear nueva recompensa
    new_reward := jsonb_build_object(
        'date', CURRENT_DATE::TEXT,
        'type', reward_type,
        'reward', reward_data,
        'streak_count', streak_count,
        'claimed_at', NOW()::TEXT
    );
    
    -- Agregar a la lista de recompensas
    current_rewards := current_rewards || new_reward;
    
    -- Guardar en la base de datos
    UPDATE public.astrade_user_profiles 
    SET daily_rewards_claimed = current_rewards, updated_at = NOW()
    WHERE user_id = user_uuid;
    
    -- Construir respuesta
    result := jsonb_build_object(
        'reward_recorded', true,
        'reward_data', new_reward,
        'total_rewards', jsonb_array_length(current_rewards)
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener estadísticas de recompensas del usuario
CREATE OR REPLACE FUNCTION get_user_rewards_stats(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    profile_record RECORD;
    result JSON;
BEGIN
    -- Obtener perfil completo
    SELECT * INTO profile_record 
    FROM public.astrade_user_profiles 
    WHERE user_id = user_uuid;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object('error', 'User profile not found');
    END IF;
    
    -- Construir estadísticas
    result := jsonb_build_object(
        'user_id', profile_record.user_id,
        'level', profile_record.level,
        'experience', profile_record.experience,
        'total_trades', profile_record.total_trades,
        'total_pnl', profile_record.total_pnl,
        'streaks', profile_record.streaks,
        'achievements', profile_record.achievements,
        'total_rewards_claimed', jsonb_array_length(profile_record.daily_rewards_claimed),
        'recent_rewards', profile_record.daily_rewards_claimed #-> -10,
        'created_at', profile_record.created_at,
        'updated_at', profile_record.updated_at
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 