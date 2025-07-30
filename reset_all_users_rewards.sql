-- =====================================================
-- REINICIAR RECOMPENSAS DE TODOS LOS USUARIOS
-- =====================================================
-- Ejecutar este script en Supabase Dashboard > SQL Editor
-- ⚠️ ADVERTENCIA: Esto eliminará todo el progreso de recompensas de todos los usuarios

-- 1. Limpiar todas las recompensas diarias reclamadas
UPDATE public.astrade_user_profiles 
SET daily_rewards_claimed = '[]'::jsonb
WHERE daily_rewards_claimed IS NOT NULL;

-- 2. Reiniciar todos los streaks a 0
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
WHERE streaks IS NOT NULL;

-- 3. Limpiar tabla de daily_rewards (si existe)
DELETE FROM public.daily_rewards;

-- 4. Limpiar tabla de user_streaks (si existe)
DELETE FROM public.user_streaks;

-- 5. Verificar los cambios
SELECT 
    user_id,
    display_name,
    streaks,
    daily_rewards_claimed
FROM public.astrade_user_profiles 
LIMIT 5;

-- 6. Mostrar resumen de usuarios afectados
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN streaks IS NOT NULL THEN 1 END) as users_with_streaks,
    COUNT(CASE WHEN daily_rewards_claimed IS NOT NULL THEN 1 END) as users_with_rewards
FROM public.astrade_user_profiles;

-- 7. Verificar que las tablas están limpias
SELECT 'daily_rewards' as table_name, COUNT(*) as record_count FROM public.daily_rewards
UNION ALL
SELECT 'user_streaks' as table_name, COUNT(*) as record_count FROM public.user_streaks; 