-- ============================================
-- PLANETS SCHEMA MIGRATION - SAFE VERSION
-- This version handles existing tables and adds missing columns
-- ============================================

-- First, let's create tables if they don't exist (basic structure)
CREATE TABLE IF NOT EXISTS public.planets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) NOT NULL,
    order_index INTEGER,
    total_quizzes INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.quizzes (
    id SERIAL PRIMARY KEY,
    planet_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    quiz_code VARCHAR(10) NOT NULL,
    order_index INTEGER,
    total_questions INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL DEFAULT 'A',
    explanation TEXT,
    order_index INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_planet_progress (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    planet_id INTEGER NOT NULL,
    completed_quizzes INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT false,
    first_completed_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_quiz_progress (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    quiz_id INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    is_completed BOOLEAN DEFAULT false,
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    attempts INTEGER DEFAULT 0,
    first_attempt_at TIMESTAMP WITH TIME ZONE,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    best_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_question_attempts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    question_id INTEGER NOT NULL,
    quiz_attempt_id INTEGER,
    selected_answer CHAR(1) NOT NULL DEFAULT 'A',
    is_correct BOOLEAN NOT NULL DEFAULT false,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_time_seconds INTEGER
);

-- Now safely add missing columns if they don't exist
DO $$
BEGIN
    -- Add missing columns to planets
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'planets' AND column_name = 'order_index'
    ) THEN
        ALTER TABLE public.planets ADD COLUMN order_index INTEGER;
    END IF;

    -- Add missing columns to quizzes
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quizzes' AND column_name = 'order_index'
    ) THEN
        ALTER TABLE public.quizzes ADD COLUMN order_index INTEGER;
    END IF;

    -- Add quiz_code column to quizzes if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quizzes' AND column_name = 'quiz_code'
    ) THEN
        ALTER TABLE public.quizzes ADD COLUMN quiz_code VARCHAR(10) NOT NULL DEFAULT '1A';
    END IF;

    -- Add missing columns to questions
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'order_index'
    ) THEN
        ALTER TABLE public.questions ADD COLUMN order_index INTEGER;
    END IF;

    -- Add correct_answer column to questions if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'correct_answer'
    ) THEN
        ALTER TABLE public.questions ADD COLUMN correct_answer CHAR(1) NOT NULL DEFAULT 'A';
    END IF;

    -- Add selected_answer column to user_question_attempts if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_question_attempts' AND column_name = 'selected_answer'
    ) THEN
        ALTER TABLE public.user_question_attempts ADD COLUMN selected_answer CHAR(1) NOT NULL DEFAULT 'A';
    END IF;

    -- Add is_correct column to user_question_attempts if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_question_attempts' AND column_name = 'is_correct'
    ) THEN
        ALTER TABLE public.user_question_attempts ADD COLUMN is_correct BOOLEAN NOT NULL DEFAULT false;
    END IF;

    -- Add completion_percentage column to user_quiz_progress if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_quiz_progress' AND column_name = 'completion_percentage'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD COLUMN completion_percentage DECIMAL(5,2) DEFAULT 0.00;
    END IF;

    -- Add attempts column to user_quiz_progress if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_quiz_progress' AND column_name = 'attempts'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD COLUMN attempts INTEGER DEFAULT 0;
    END IF;

    -- Add first_attempt_at column to user_quiz_progress if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_quiz_progress' AND column_name = 'first_attempt_at'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD COLUMN first_attempt_at TIMESTAMP WITH TIME ZONE;
    END IF;

    -- Add last_attempt_at column to user_quiz_progress if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_quiz_progress' AND column_name = 'last_attempt_at'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD COLUMN last_attempt_at TIMESTAMP WITH TIME ZONE;
    END IF;

    -- Add best_score column to user_quiz_progress if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_quiz_progress' AND column_name = 'best_score'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD COLUMN best_score INTEGER DEFAULT 0;
    END IF;

    -- Add quiz_attempt_id column to user_question_attempts if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_question_attempts' AND column_name = 'quiz_attempt_id'
    ) THEN
        ALTER TABLE public.user_question_attempts ADD COLUMN quiz_attempt_id INTEGER;
    END IF;

    -- Add response_time_seconds column to user_question_attempts if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_question_attempts' AND column_name = 'response_time_seconds'
    ) THEN
        ALTER TABLE public.user_question_attempts ADD COLUMN response_time_seconds INTEGER;
    END IF;

    -- Add missing core columns to ensure compatibility
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'option_a'
    ) THEN
        ALTER TABLE public.questions ADD COLUMN option_a TEXT NOT NULL DEFAULT '';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'option_b'
    ) THEN
        ALTER TABLE public.questions ADD COLUMN option_b TEXT NOT NULL DEFAULT '';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'option_c'
    ) THEN
        ALTER TABLE public.questions ADD COLUMN option_c TEXT NOT NULL DEFAULT '';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'option_d'
    ) THEN
        ALTER TABLE public.questions ADD COLUMN option_d TEXT NOT NULL DEFAULT '';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'explanation'
    ) THEN
        ALTER TABLE public.questions ADD COLUMN explanation TEXT;
    END IF;

    -- Add missing columns to planets
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'planets' AND column_name = 'description'
    ) THEN
        ALTER TABLE public.planets ADD COLUMN description TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'planets' AND column_name = 'color'
    ) THEN
        ALTER TABLE public.planets ADD COLUMN color VARCHAR(7) NOT NULL DEFAULT '#000000';
    END IF;

    -- Add missing columns to quizzes
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quizzes' AND column_name = 'description'
    ) THEN
        ALTER TABLE public.quizzes ADD COLUMN description TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quizzes' AND column_name = 'title'
    ) THEN
        ALTER TABLE public.quizzes ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT 'Untitled Quiz';
    END IF;
END $$;

-- Add constraints safely
DO $$
BEGIN
    -- Add unique constraint to planets.name if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'planets' AND constraint_name = 'planets_name_key'
    ) THEN
        ALTER TABLE public.planets ADD CONSTRAINT planets_name_key UNIQUE (name);
    END IF;

    -- Add unique constraint to planets.order_index if it doesn't exist and column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'planets' AND constraint_name = 'planets_order_index_key'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'planets' AND column_name = 'order_index'
    ) THEN
        ALTER TABLE public.planets ADD CONSTRAINT planets_order_index_key UNIQUE (order_index);
    END IF;

    -- Add check constraint to questions.correct_answer if it doesn't exist and column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'questions_correct_answer_check'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'correct_answer'
    ) THEN
        ALTER TABLE public.questions ADD CONSTRAINT questions_correct_answer_check 
        CHECK (correct_answer IN ('A', 'B', 'C', 'D'));
    END IF;

    -- Add check constraint to user_question_attempts.selected_answer if it doesn't exist and column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'user_question_attempts_selected_answer_check'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_question_attempts' AND column_name = 'selected_answer'
    ) THEN
        ALTER TABLE public.user_question_attempts ADD CONSTRAINT user_question_attempts_selected_answer_check 
        CHECK (selected_answer IN ('A', 'B', 'C', 'D'));
    END IF;
END $$;

-- Add foreign key constraints safely
DO $$
BEGIN
    -- Add foreign key from quizzes to planets if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'quizzes' AND constraint_name = 'quizzes_planet_id_fkey'
    ) THEN
        ALTER TABLE public.quizzes ADD CONSTRAINT quizzes_planet_id_fkey 
        FOREIGN KEY (planet_id) REFERENCES public.planets(id) ON DELETE CASCADE;
    END IF;

    -- Add foreign key from questions to quizzes if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questions' AND constraint_name = 'questions_quiz_id_fkey'
    ) THEN
        ALTER TABLE public.questions ADD CONSTRAINT questions_quiz_id_fkey 
        FOREIGN KEY (quiz_id) REFERENCES public.quizzes(id) ON DELETE CASCADE;
    END IF;

    -- Add foreign key from user_planet_progress to auth.users if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_planet_progress' AND constraint_name = 'user_planet_progress_user_id_fkey'
    ) THEN
        ALTER TABLE public.user_planet_progress ADD CONSTRAINT user_planet_progress_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;

    -- Add foreign key from user_planet_progress to planets if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_planet_progress' AND constraint_name = 'user_planet_progress_planet_id_fkey'
    ) THEN
        ALTER TABLE public.user_planet_progress ADD CONSTRAINT user_planet_progress_planet_id_fkey 
        FOREIGN KEY (planet_id) REFERENCES public.planets(id) ON DELETE CASCADE;
    END IF;

    -- Add foreign key from user_quiz_progress to auth.users if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_quiz_progress' AND constraint_name = 'user_quiz_progress_user_id_fkey'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD CONSTRAINT user_quiz_progress_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;

    -- Add foreign key from user_quiz_progress to quizzes if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_quiz_progress' AND constraint_name = 'user_quiz_progress_quiz_id_fkey'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD CONSTRAINT user_quiz_progress_quiz_id_fkey 
        FOREIGN KEY (quiz_id) REFERENCES public.quizzes(id) ON DELETE CASCADE;
    END IF;

    -- Add foreign key from user_question_attempts to auth.users if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_question_attempts' AND constraint_name = 'user_question_attempts_user_id_fkey'
    ) THEN
        ALTER TABLE public.user_question_attempts ADD CONSTRAINT user_question_attempts_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;

    -- Add foreign key from user_question_attempts to questions if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_question_attempts' AND constraint_name = 'user_question_attempts_question_id_fkey'
    ) THEN
        ALTER TABLE public.user_question_attempts ADD CONSTRAINT user_question_attempts_question_id_fkey 
        FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add unique constraints for composite keys safely
DO $$
BEGIN
    -- Add unique constraint to quizzes (planet_id, quiz_code) if it doesn't exist and columns exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'quizzes' AND constraint_name = 'quizzes_planet_id_quiz_code_key'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quizzes' AND column_name = 'quiz_code'
    ) THEN
        ALTER TABLE public.quizzes ADD CONSTRAINT quizzes_planet_id_quiz_code_key 
        UNIQUE (planet_id, quiz_code);
    END IF;

    -- Add unique constraint to quizzes (planet_id, order_index) if it doesn't exist and columns exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'quizzes' AND constraint_name = 'quizzes_planet_id_order_index_key'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quizzes' AND column_name = 'order_index'
    ) THEN
        ALTER TABLE public.quizzes ADD CONSTRAINT quizzes_planet_id_order_index_key 
        UNIQUE (planet_id, order_index);
    END IF;

    -- Add unique constraint to questions (quiz_id, order_index) if it doesn't exist and columns exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'questions' AND constraint_name = 'questions_quiz_id_order_index_key'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'order_index'
    ) THEN
        ALTER TABLE public.questions ADD CONSTRAINT questions_quiz_id_order_index_key 
        UNIQUE (quiz_id, order_index);
    END IF;

    -- Add unique constraint to user_planet_progress (user_id, planet_id) if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_planet_progress' AND constraint_name = 'user_planet_progress_user_id_planet_id_key'
    ) THEN
        ALTER TABLE public.user_planet_progress ADD CONSTRAINT user_planet_progress_user_id_planet_id_key 
        UNIQUE (user_id, planet_id);
    END IF;

    -- Add unique constraint to user_quiz_progress (user_id, quiz_id) if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_quiz_progress' AND constraint_name = 'user_quiz_progress_user_id_quiz_id_key'
    ) THEN
        ALTER TABLE public.user_quiz_progress ADD CONSTRAINT user_quiz_progress_user_id_quiz_id_key 
        UNIQUE (user_id, quiz_id);
    END IF;
END $$;

-- Create indexes for better performance (only if they don't exist)
CREATE INDEX IF NOT EXISTS idx_planets_order ON public.planets(order_index);
CREATE INDEX IF NOT EXISTS idx_quizzes_planet_id ON public.quizzes(planet_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_order ON public.quizzes(planet_id, order_index);
CREATE INDEX IF NOT EXISTS idx_questions_quiz_id ON public.questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_questions_order ON public.questions(quiz_id, order_index);
CREATE INDEX IF NOT EXISTS idx_user_planet_progress_user ON public.user_planet_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_planet_progress_planet ON public.user_planet_progress(planet_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_progress_user ON public.user_quiz_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_progress_quiz ON public.user_quiz_progress(quiz_id);
CREATE INDEX IF NOT EXISTS idx_user_question_attempts_user ON public.user_question_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_question_attempts_question ON public.user_question_attempts(question_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.planets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_planet_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_quiz_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_question_attempts ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies (drop if exists, then recreate)
DROP POLICY IF EXISTS "Anyone can view planets" ON public.planets;
DROP POLICY IF EXISTS "Anyone can view quizzes" ON public.quizzes;
DROP POLICY IF EXISTS "Anyone can view questions" ON public.questions;
DROP POLICY IF EXISTS "Users can manage their own planet progress" ON public.user_planet_progress;
DROP POLICY IF EXISTS "Users can manage their own quiz progress" ON public.user_quiz_progress;
DROP POLICY IF EXISTS "Users can manage their own question attempts" ON public.user_question_attempts;

-- RLS Policies for planets, quizzes, and questions (public read access)
CREATE POLICY "Anyone can view planets" ON public.planets FOR SELECT USING (true);
CREATE POLICY "Anyone can view quizzes" ON public.quizzes FOR SELECT USING (true);
CREATE POLICY "Anyone can view questions" ON public.questions FOR SELECT USING (true);

-- RLS Policies for user progress (users can only see their own progress)
CREATE POLICY "Users can manage their own planet progress" 
ON public.user_planet_progress 
FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage their own quiz progress" 
ON public.user_quiz_progress 
FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage their own question attempts" 
ON public.user_question_attempts 
FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Create or replace functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing triggers if they exist, then recreate
DROP TRIGGER IF EXISTS update_planets_updated_at ON public.planets;
DROP TRIGGER IF EXISTS update_quizzes_updated_at ON public.quizzes;
DROP TRIGGER IF EXISTS update_questions_updated_at ON public.questions;
DROP TRIGGER IF EXISTS update_user_planet_progress_updated_at ON public.user_planet_progress;
DROP TRIGGER IF EXISTS update_user_quiz_progress_updated_at ON public.user_quiz_progress;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_planets_updated_at BEFORE UPDATE ON public.planets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quizzes_updated_at BEFORE UPDATE ON public.quizzes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON public.questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_planet_progress_updated_at BEFORE UPDATE ON public.user_planet_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_quiz_progress_updated_at BEFORE UPDATE ON public.user_quiz_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically update planet progress when quiz is completed
CREATE OR REPLACE FUNCTION update_planet_progress_on_quiz_completion()
RETURNS TRIGGER AS $$
BEGIN
    -- Only proceed if quiz is being marked as completed for the first time
    IF NEW.is_completed = true AND (OLD.is_completed = false OR OLD.is_completed IS NULL) THEN
        -- Update or insert planet progress
        INSERT INTO public.user_planet_progress (user_id, planet_id, completed_quizzes, total_score, last_activity_at)
        SELECT 
            NEW.user_id,
            q.planet_id,
            1,
            NEW.score,
            NOW()
        FROM public.quizzes q
        WHERE q.id = NEW.quiz_id
        ON CONFLICT (user_id, planet_id) 
        DO UPDATE SET
            completed_quizzes = user_planet_progress.completed_quizzes + 1,
            total_score = user_planet_progress.total_score + NEW.score,
            last_activity_at = NOW(),
            updated_at = NOW();
            
        -- Check if planet is now completed (all quizzes done)
        UPDATE public.user_planet_progress 
        SET 
            is_completed = true,
            first_completed_at = CASE 
                WHEN first_completed_at IS NULL THEN NOW() 
                ELSE first_completed_at 
            END
        WHERE user_id = NEW.user_id 
        AND planet_id = (SELECT planet_id FROM public.quizzes WHERE id = NEW.quiz_id)
        AND completed_quizzes >= (
            SELECT COUNT(*) 
            FROM public.quizzes q2 
            WHERE q2.planet_id = (SELECT planet_id FROM public.quizzes WHERE id = NEW.quiz_id)
            AND q2.is_active = true
        );
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update quiz totals when questions are added/removed
CREATE OR REPLACE FUNCTION update_quiz_question_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.quizzes 
        SET total_questions = total_questions + 1,
            updated_at = NOW()
        WHERE id = NEW.quiz_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.quizzes 
        SET total_questions = total_questions - 1,
            updated_at = NOW()
        WHERE id = OLD.quiz_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Function to update planet quiz totals
CREATE OR REPLACE FUNCTION update_planet_quiz_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.planets 
        SET total_quizzes = total_quizzes + 1,
            updated_at = NOW()
        WHERE id = NEW.planet_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.planets 
        SET total_quizzes = total_quizzes - 1,
            updated_at = NOW()
        WHERE id = OLD.planet_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Drop existing triggers if they exist, then recreate
DROP TRIGGER IF EXISTS update_planet_progress_on_quiz_completion_trigger ON public.user_quiz_progress;
DROP TRIGGER IF EXISTS update_quiz_question_count_insert_trigger ON public.questions;
DROP TRIGGER IF EXISTS update_quiz_question_count_delete_trigger ON public.questions;
DROP TRIGGER IF EXISTS update_planet_quiz_count_insert_trigger ON public.quizzes;
DROP TRIGGER IF EXISTS update_planet_quiz_count_delete_trigger ON public.quizzes;

-- Create triggers for automatic progress and count updates
CREATE TRIGGER update_planet_progress_on_quiz_completion_trigger
    AFTER UPDATE ON public.user_quiz_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_planet_progress_on_quiz_completion();

CREATE TRIGGER update_quiz_question_count_insert_trigger
    AFTER INSERT ON public.questions
    FOR EACH ROW
    EXECUTE FUNCTION update_quiz_question_count();

CREATE TRIGGER update_quiz_question_count_delete_trigger
    AFTER DELETE ON public.questions
    FOR EACH ROW
    EXECUTE FUNCTION update_quiz_question_count();

CREATE TRIGGER update_planet_quiz_count_insert_trigger
    AFTER INSERT ON public.quizzes
    FOR EACH ROW
    EXECUTE FUNCTION update_planet_quiz_count();

CREATE TRIGGER update_planet_quiz_count_delete_trigger
    AFTER DELETE ON public.quizzes
    FOR EACH ROW
    EXECUTE FUNCTION update_planet_quiz_count(); 