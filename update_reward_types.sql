-- Script para cambiar todas las referencias de "card" a "nft" en las recompensas
-- Ejecutar en Supabase Dashboard > SQL Editor

-- Actualizar día 3: mystery_card -> mystery_nft
UPDATE public.reward_configs 
SET reward_data = jsonb_set(
    reward_data, 
    '{type}', 
    '"mystery_nft"'
)
WHERE day_number = 3;

-- Actualizar descripción del día 3
UPDATE public.reward_configs 
SET reward_data = jsonb_set(
    reward_data, 
    '{description}', 
    '"Día 3 - NFT Misterioso"'
)
WHERE day_number = 3;

-- Verificar cambios
SELECT day_number, reward_data 
FROM public.reward_configs 
WHERE day_number IN (2, 3, 4, 6) 
ORDER BY day_number; 