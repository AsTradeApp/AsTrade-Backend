-- =====================================================
-- AS TRADE BACKEND - COMPLETE DATABASE SETUP
-- =====================================================
-- Ejecutar este archivo en el SQL Editor de Supabase
-- para crear todas las tablas necesarias del backend

-- =====================================================
-- 1. TABLAS PRINCIPALES DE USUARIOS
-- =====================================================

-- Tabla de wallets de usuarios
CREATE TABLE IF NOT EXISTS public.user_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    network TEXT NOT NULL DEFAULT 'sepolia',
    transaction_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de credenciales de usuarios
CREATE TABLE IF NOT EXISTS public.astrade_user_credentials (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    extended_api_key VARCHAR,
    extended_secret_key VARCHAR,
    extended_stark_private_key TEXT NOT NULL,
    environment VARCHAR DEFAULT 'testnet' CHECK (environment IN ('testnet', 'mainnet')),
    is_mock_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de perfiles de usuarios (gamificación)
CREATE TABLE IF NOT EXISTS public.astrade_user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name VARCHAR,
    avatar_url TEXT,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    total_pnl NUMERIC DEFAULT 0,
    achievements JSONB DEFAULT '[]',
    streaks JSONB DEFAULT '{"daily_login": {"current_streak": 0, "longest_streak": 0, "last_activity_date": null}, "galaxy_explorer": {"current_streak": 0, "longest_streak": 0, "last_activity_date": null}}',
    daily_rewards_claimed JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 2. TABLAS DE RECOMPENSAS
-- =====================================================

-- Configuración de recompensas
CREATE TABLE IF NOT EXISTS public.reward_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reward_type VARCHAR NOT NULL,
    day_number INTEGER,
    reward_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- NFTs de usuarios
CREATE TABLE IF NOT EXISTS public.user_nfts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    nft_type VARCHAR NOT NULL,
    nft_name VARCHAR NOT NULL,
    nft_description TEXT,
    image_url TEXT NOT NULL,
    rarity VARCHAR DEFAULT 'common',
    acquired_date DATE DEFAULT CURRENT_DATE,
    acquired_from VARCHAR,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. TABLAS DE PLANETAS Y QUIZZES
-- =====================================================

-- Secuencia para IDs de planetas
CREATE SEQUENCE IF NOT EXISTS public.planets_id_seq;

-- Tabla de planetas
CREATE TABLE IF NOT EXISTS public.planets (
    id INTEGER PRIMARY KEY DEFAULT nextval('planets_id_seq'),
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR NOT NULL,
    order_index INTEGER UNIQUE,
    total_quizzes INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Secuencia para IDs de quizzes
CREATE SEQUENCE IF NOT EXISTS public.quizzes_id_seq;

-- Tabla de quizzes
CREATE TABLE IF NOT EXISTS public.quizzes (
    id INTEGER PRIMARY KEY DEFAULT nextval('quizzes_id_seq'),
    planet_id INTEGER REFERENCES public.planets(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    title VARCHAR NOT NULL DEFAULT 'Untitled Quiz',
    slug VARCHAR NOT NULL,
    description TEXT,
    quiz_code VARCHAR NOT NULL DEFAULT '1A',
    order_index INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Secuencia para IDs de preguntas
CREATE SEQUENCE IF NOT EXISTS public.questions_id_seq;

-- Tabla de preguntas
CREATE TABLE IF NOT EXISTS public.questions (
    id INTEGER PRIMARY KEY DEFAULT nextval('questions_id_seq'),
    quiz_id INTEGER REFERENCES public.quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL DEFAULT '',
    option_b TEXT NOT NULL DEFAULT '',
    option_c TEXT NOT NULL DEFAULT '',
    option_d TEXT NOT NULL DEFAULT '',
    correct_answer CHAR(1) NOT NULL DEFAULT 'A' CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    order_index INTEGER,
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de opciones de preguntas (deprecated pero mantenida por compatibilidad)
CREATE TABLE IF NOT EXISTS public.question_options (
    id INTEGER PRIMARY KEY DEFAULT nextval('question_options_id_seq'),
    question_id INTEGER REFERENCES public.questions(id) ON DELETE CASCADE,
    option_letter VARCHAR NOT NULL CHECK (option_letter IN ('A', 'B', 'C', 'D')),
    option_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Secuencia para question_options
CREATE SEQUENCE IF NOT EXISTS public.question_options_id_seq;

-- =====================================================
-- 4. TABLAS DE PROGRESO DE USUARIOS
-- =====================================================

-- Secuencia para user_planet_progress
CREATE SEQUENCE IF NOT EXISTS public.user_planet_progress_id_seq;

-- Progreso de usuarios en planetas
CREATE TABLE IF NOT EXISTS public.user_planet_progress (
    id INTEGER PRIMARY KEY DEFAULT nextval('user_planet_progress_id_seq'),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    planet_id INTEGER REFERENCES public.planets(id) ON DELETE CASCADE,
    is_unlocked BOOLEAN DEFAULT false,
    is_completed BOOLEAN DEFAULT false,
    quizzes_completed INTEGER DEFAULT 0,
    total_quizzes INTEGER DEFAULT 2,
    experience_earned INTEGER DEFAULT 0,
    unlocked_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Secuencia para user_quiz_progress
CREATE SEQUENCE IF NOT EXISTS public.user_quiz_progress_id_seq;

-- Progreso de usuarios en quizzes
CREATE TABLE IF NOT EXISTS public.user_quiz_progress (
    id INTEGER PRIMARY KEY DEFAULT nextval('user_quiz_progress_id_seq'),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES public.quizzes(id) ON DELETE CASCADE,
    is_completed BOOLEAN DEFAULT false,
    best_score INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    completion_percentage NUMERIC DEFAULT 0.00,
    first_attempt_at TIMESTAMP WITH TIME ZONE,
    first_completed_at TIMESTAMP WITH TIME ZONE,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Secuencia para user_quiz_attempts
CREATE SEQUENCE IF NOT EXISTS public.user_quiz_attempts_id_seq;

-- Intentos de quizzes de usuarios
CREATE TABLE IF NOT EXISTS public.user_quiz_attempts (
    id INTEGER PRIMARY KEY DEFAULT nextval('user_quiz_attempts_id_seq'),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES public.quizzes(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    time_taken_seconds INTEGER,
    answers JSONB NOT NULL,
    is_completed BOOLEAN DEFAULT true,
    xp_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Secuencia para user_question_attempts
CREATE SEQUENCE IF NOT EXISTS public.user_question_attempts_id_seq;

-- Intentos de preguntas individuales
CREATE TABLE IF NOT EXISTS public.user_question_attempts (
    id INTEGER PRIMARY KEY DEFAULT nextval('user_question_attempts_id_seq'),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES public.questions(id) ON DELETE CASCADE,
    quiz_attempt_id INTEGER,
    selected_answer CHAR(1) NOT NULL DEFAULT 'A' CHECK (selected_answer IN ('A', 'B', 'C', 'D')),
    is_correct BOOLEAN NOT NULL DEFAULT false,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_time_seconds INTEGER
);

-- =====================================================
-- 5. HABILITAR ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE public.user_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.astrade_user_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.astrade_user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reward_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_nfts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.planets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.question_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_planet_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_quiz_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_question_attempts ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 6. POLÍTICAS RLS
-- =====================================================

-- Políticas para user_wallets
CREATE POLICY "Users can view own wallet" ON public.user_wallets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own wallet" ON public.user_wallets FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own wallet" ON public.user_wallets FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para astrade_user_credentials
CREATE POLICY "Users can view own credentials" ON public.astrade_user_credentials FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own credentials" ON public.astrade_user_credentials FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own credentials" ON public.astrade_user_credentials FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para astrade_user_profiles
CREATE POLICY "Users can view own profile" ON public.astrade_user_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON public.astrade_user_profiles FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON public.astrade_user_profiles FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para reward_configs (lectura pública)
CREATE POLICY "Anyone can view reward configs" ON public.reward_configs FOR SELECT USING (true);

-- Políticas para user_nfts
CREATE POLICY "Users can view own NFTs" ON public.user_nfts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own NFTs" ON public.user_nfts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own NFTs" ON public.user_nfts FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para planets (lectura pública)
CREATE POLICY "Anyone can view planets" ON public.planets FOR SELECT USING (true);

-- Políticas para quizzes (lectura pública)
CREATE POLICY "Anyone can view quizzes" ON public.quizzes FOR SELECT USING (true);

-- Políticas para questions (lectura pública)
CREATE POLICY "Anyone can view questions" ON public.questions FOR SELECT USING (true);

-- Políticas para question_options (lectura pública)
CREATE POLICY "Anyone can view question options" ON public.question_options FOR SELECT USING (true);

-- Políticas para user_planet_progress
CREATE POLICY "Users can view own planet progress" ON public.user_planet_progress FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own planet progress" ON public.user_planet_progress FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own planet progress" ON public.user_planet_progress FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para user_quiz_progress
CREATE POLICY "Users can view own quiz progress" ON public.user_quiz_progress FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own quiz progress" ON public.user_quiz_progress FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own quiz progress" ON public.user_quiz_progress FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para user_quiz_attempts
CREATE POLICY "Users can view own quiz attempts" ON public.user_quiz_attempts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own quiz attempts" ON public.user_quiz_attempts FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Políticas para user_question_attempts
CREATE POLICY "Users can view own question attempts" ON public.user_question_attempts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own question attempts" ON public.user_question_attempts FOR INSERT WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- 7. FUNCIONES Y TRIGGERS
-- =====================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_user_wallets_updated_at BEFORE UPDATE ON public.user_wallets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_astrade_user_credentials_updated_at BEFORE UPDATE ON public.astrade_user_credentials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_astrade_user_profiles_updated_at BEFORE UPDATE ON public.astrade_user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_nfts_updated_at BEFORE UPDATE ON public.user_nfts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_planets_updated_at BEFORE UPDATE ON public.planets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_quizzes_updated_at BEFORE UPDATE ON public.quizzes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON public.questions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_planet_progress_updated_at BEFORE UPDATE ON public.user_planet_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_quiz_progress_updated_at BEFORE UPDATE ON public.user_quiz_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 8. ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_user_wallets_user_id ON public.user_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_user_nfts_user_id ON public.user_nfts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_nfts_nft_type ON public.user_nfts(nft_type);
CREATE INDEX IF NOT EXISTS idx_user_nfts_rarity ON public.user_nfts(rarity);
CREATE INDEX IF NOT EXISTS idx_quizzes_planet_id ON public.quizzes(planet_id);
CREATE INDEX IF NOT EXISTS idx_questions_quiz_id ON public.questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_user_planet_progress_user_id ON public.user_planet_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_planet_progress_planet_id ON public.user_planet_progress(planet_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_progress_user_id ON public.user_quiz_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_progress_quiz_id ON public.user_quiz_progress(quiz_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_attempts_user_id ON public.user_quiz_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_attempts_quiz_id ON public.user_quiz_attempts(quiz_id);
CREATE INDEX IF NOT EXISTS idx_user_question_attempts_user_id ON public.user_question_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_question_attempts_question_id ON public.user_question_attempts(question_id);

-- =====================================================
-- ¡BASE DE DATOS CONFIGURADA COMPLETAMENTE!
-- =====================================================
-- Ahora puedes ejecutar el backend con: docker-compose up -d 