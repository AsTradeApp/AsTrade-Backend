-- =====================================================
-- RESTAURAR DATOS DE LA TABLA reward_configs
-- =====================================================
-- Ejecutar este script en Supabase Dashboard > SQL Editor

-- Limpiar tabla (opcional, solo si quieres empezar desde cero)
-- DELETE FROM public.reward_configs;

-- Insertar configuración de recompensas por defecto
INSERT INTO public.reward_configs (reward_type, day_number, reward_data, is_active) VALUES
('daily_streak', 1, '{"amount": 50, "currency": "credits", "type": "credits", "description": "Día 1 - Créditos"}', true),
('daily_streak', 2, '{"amount": 75, "currency": "credits", "type": "credits", "description": "Día 2 - Créditos", "image_url": "/static/images/rewards/day-2.png"}', true),
('daily_streak', 3, '{"amount": 100, "currency": "credits", "type": "mystery_card", "description": "Día 3 - Carta Misteriosa"}', true),
('daily_streak', 4, '{"amount": 125, "currency": "credits", "type": "credits", "description": "Día 4 - Créditos", "image_url": "/static/images/rewards/day-4.png"}', true),
('daily_streak', 5, '{"amount": 150, "currency": "credits", "type": "credits", "description": "Día 5 - Créditos"}', true),
('daily_streak', 6, '{"amount": 200, "currency": "credits", "type": "credits", "description": "Día 6 - Créditos", "image_url": "/static/images/rewards/day-6.png"}', true),
('daily_streak', 7, '{"amount": 500, "currency": "credits", "type": "premium_mystery_variant", "description": "Día 7 - Variante Premium Misteriosa"}', true),
('galaxy_explorer', NULL, '{"amount": 25, "currency": "credits", "type": "galaxy_credits", "description": "Explorador de Galaxia"}', true)
ON CONFLICT (reward_type, day_number) DO NOTHING;

-- Verificar que se insertaron correctamente
SELECT 
    reward_type, 
    day_number, 
    reward_data,
    is_active,
    created_at
FROM public.reward_configs 
ORDER BY reward_type, day_number;

-- Mostrar resumen
SELECT 
    COUNT(*) as total_configs,
    COUNT(CASE WHEN reward_type = 'daily_streak' THEN 1 END) as daily_streak_configs,
    COUNT(CASE WHEN reward_type = 'galaxy_explorer' THEN 1 END) as galaxy_explorer_configs
FROM public.reward_configs; 