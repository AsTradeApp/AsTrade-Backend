-- =====================================================
-- REINICIAR RECOMPENSAS DE UN USUARIO ESPECÍFICO
-- =====================================================
-- Ejecutar este script en Supabase Dashboard > SQL Editor

-- Reemplazar 'USER_ID_AQUI' con el ID del usuario específico
-- Ejemplo: fb16ec78-ff70-4895-9ace-92a1d8202fdb

-- 1. Reiniciar recompensas diarias del usuario específico
UPDATE public.astrade_user_profiles 
SET daily_rewards_claimed = '[]'::jsonb
WHERE user_id = 'fb16ec78-ff70-4895-9ace-92a1d8202fdb';

-- 2. Reiniciar streaks del usuario específico
UPDATE public.astrade_user_profiles 
SET streaks = jsonb_build_object(
    'daily_login', jsonb_build_object(
        'current_streak', 0,
        'longest_streak', 0,
        'last_activity_date', null
    ),
    'galaxy_explorer', jsonb_build_object(
        'current_streak', 0,
        'longest_streak', 0,
        'last_activity_date', null
    )
)
WHERE user_id = 'fb16ec78-ff70-4895-9ace-92a1d8202fdb';

-- 3. Verificar el cambio
SELECT 
    user_id,
    display_name,
    streaks,
    daily_rewards_claimed
FROM public.astrade_user_profiles 
WHERE user_id = 'fb16ec78-ff70-4895-9ace-92a1d8202fdb'; 