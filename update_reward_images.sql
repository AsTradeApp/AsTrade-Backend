-- Script para actualizar las URLs de imágenes de recompensas
-- Ejecutar en Supabase Dashboard > SQL Editor

-- Actualizar día 2: Bandera Extended
UPDATE public.reward_configs 
SET reward_data = jsonb_set(
    reward_data, 
    '{image_url}', 
    '"/static/images/rewards/day-2.png"'
)
WHERE day_number = 2;

-- Actualizar día 4: Icono circular azul
UPDATE public.reward_configs 
SET reward_data = jsonb_set(
    reward_data, 
    '{image_url}', 
    '"/static/images/rewards/day-4.png"'
)
WHERE day_number = 4;

-- Actualizar día 6: Gorra amarilla "Stwo"
UPDATE public.reward_configs 
SET reward_data = jsonb_set(
    reward_data, 
    '{image_url}', 
    '"/static/images/rewards/day-6.png"'
)
WHERE day_number = 6;

-- Verificar cambios
SELECT day_number, reward_data 
FROM public.reward_configs 
WHERE day_number IN (2, 4, 6) 
ORDER BY day_number; 