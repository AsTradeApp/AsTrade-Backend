#!/usr/bin/env python3
"""
Seed script for planets and quiz data from PLANET_QUIZES.md
This script parses the markdown file and populates the Supabase database
"""
import os
import sys
import asyncio
from typing import List, Dict, Any
import re

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.database import get_supabase_client
from app.models.planets import AnswerOption


class PlanetsDataSeeder:
    """Seeder for planets and quiz data"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.planets_data = []
    
    def parse_quiz_markdown(self, file_path: str):
        """Parse the PLANET_QUIZES.md file to extract quiz data"""
        print(f"Parsing quiz data from {file_path}")
        
        # Define planet mapping
        planet_mapping = {
            "PLANET 1: MERCURY": {
                "name": "Mercury",
                "description": "Foundation Basics - Learn the fundamentals of trading",
                "color": "#F43F5E",  # Red/pink for Mercury
                "order_index": 1
            },
            "PLANET 2: VENUS": {
                "name": "Venus", 
                "description": "Chart Reading - Master the art of technical analysis",
                "color": "#FBBF24",  # Yellow/gold for Venus
                "order_index": 2
            },
            "PLANET 3: EARTH": {
                "name": "Earth",
                "description": "Basic Strategy - Develop your trading strategies",
                "color": "#10B981",  # Green for Earth
                "order_index": 3
            },
            "PLANET 4: MARS": {
                "name": "Mars",
                "description": "Market Understanding - Understand market dynamics",
                "color": "#EF4444",  # Red for Mars
                "order_index": 4
            }
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Split by planet sections
            planet_sections = re.split(r'## 🪐 PLANET \d+:', content)[1:]  # Skip the header
            
            for i, section in enumerate(planet_sections):
                lines = section.strip().split('\n')
                if not lines:
                    continue
                
                # Extract planet info from first line
                planet_line = lines[0].strip()
                planet_key = f"PLANET {i+1}: {planet_line.split('*')[0].strip().upper()}"
                
                if planet_key not in planet_mapping:
                    print(f"Warning: Unknown planet key: {planet_key}")
                    continue
                
                planet_info = planet_mapping[planet_key]
                
                # Parse quizzes for this planet
                quizzes = self.parse_planet_quizzes(section, planet_info['order_index'])
                
                planet_data = {
                    **planet_info,
                    "quizzes": quizzes
                }
                
                self.planets_data.append(planet_data)
                print(f"Parsed planet: {planet_info['name']} with {len(quizzes)} quizzes")
        
        except Exception as e:
            print(f"Error parsing markdown file: {e}")
            raise
    
    def parse_planet_quizzes(self, planet_section: str, planet_order: int) -> List[Dict]:
        """Parse quizzes from a planet section"""
        quizzes = []
        
        # Split by quiz sections (### QUIZ)
        quiz_sections = re.split(r'### QUIZ \d+[AB]:', planet_section)[1:]
        
        for quiz_section in quiz_sections:
            lines = quiz_section.strip().split('\n')
            if not lines:
                continue
            
            # Extract quiz title from first line
            quiz_title_line = lines[0].strip()
            
            # Extract quiz code (e.g., "1A", "1B") from the section header
            quiz_match = re.search(r'QUIZ (\d+[AB]):', quiz_section)
            if not quiz_match:
                continue
            
            quiz_code = quiz_match.group(1)
            order_index = 1 if quiz_code.endswith('A') else 2
            
            # Parse questions from this quiz
            questions = self.parse_quiz_questions(quiz_section)
            
            quiz_data = {
                "title": quiz_title_line,
                "description": f"Quiz {quiz_code} for Planet {planet_order}",
                "quiz_code": quiz_code,
                "order_index": order_index,
                "questions": questions
            }
            
            quizzes.append(quiz_data)
            print(f"  Parsed quiz {quiz_code}: {quiz_title_line} with {len(questions)} questions")
        
        return quizzes
    
    def parse_quiz_questions(self, quiz_section: str) -> List[Dict]:
        """Parse questions from a quiz section"""
        questions = []
        
        # Find all questions (Q1, Q2, etc.)
        question_pattern = r'\*\*Q(\d+):\s*([^*]+)\*\*\n(.*?)(?=\*Answer:|$)'
        question_matches = re.findall(question_pattern, quiz_section, re.DOTALL)
        
        for question_num, question_text, options_text in question_matches:
            # Clean up question text
            question_text = question_text.strip()
            
            # Parse options
            option_lines = [line.strip() for line in options_text.split('\n') if line.strip()]
            options = {'A': '', 'B': '', 'C': '', 'D': ''}
            correct_answer = 'A'  # Default
            explanation = None
            
            for line in option_lines:
                if line.startswith('A)'):
                    options['A'] = line[2:].strip()
                elif line.startswith('B)'):
                    options['B'] = line[2:].strip()
                elif line.startswith('C)'):
                    options['C'] = line[2:].strip()
                elif line.startswith('D)'):
                    options['D'] = line[2:].strip()
                elif line.startswith('*Answer:'):
                    correct_answer = line.replace('*Answer:', '').strip()
            
            # Clean emojis and extra text from options
            for key in options:
                options[key] = re.sub(r'[🚀📉💰🎮📚🍎₿🏢🛡️📱🟢🔴⏰⬆️🏠💪📊🚧📉📈🕐🌊🛑🥧📋❌😤✅🐂🐻📈📉💧🏭🔄🎯]', '', options[key]).strip()
            
            question_data = {
                "question_text": question_text,
                "option_a": options['A'],
                "option_b": options['B'],
                "option_c": options['C'],
                "option_d": options['D'],
                "correct_answer": correct_answer,
                "explanation": explanation,
                "order_index": int(question_num)
            }
            
            questions.append(question_data)
        
        return questions
    
    async def seed_database(self):
        """Seed the database with parsed planet data"""
        print("Starting database seeding...")
        
        try:
            # Clear existing data (optional - comment out if you want to keep existing data)
            print("Clearing existing data...")
            self.client.table('user_question_attempts').delete().neq('id', 0).execute()
            self.client.table('user_quiz_progress').delete().neq('id', 0).execute()
            self.client.table('user_planet_progress').delete().neq('id', 0).execute()
            self.client.table('questions').delete().neq('id', 0).execute()
            self.client.table('quizzes').delete().neq('id', 0).execute()
            self.client.table('planets').delete().neq('id', 0).execute()
            
            # Seed planets and their data
            for planet_data in self.planets_data:
                print(f"Seeding planet: {planet_data['name']}")
                
                # Insert planet
                planet_insert_data = {
                    'name': planet_data['name'],
                    'description': planet_data['description'],
                    'color': planet_data['color'],
                    'order_index': planet_data['order_index'],
                    'total_quizzes': len(planet_data['quizzes']),
                    'is_active': True
                }
                
                planet_result = self.client.table('planets').insert(planet_insert_data).execute()
                planet_id = planet_result.data[0]['id']
                print(f"  Inserted planet with ID: {planet_id}")
                
                # Insert quizzes for this planet
                for quiz_data in planet_data['quizzes']:
                    print(f"    Seeding quiz: {quiz_data['quiz_code']}")
                    
                    quiz_insert_data = {
                        'planet_id': planet_id,
                        'title': quiz_data['title'],
                        'description': quiz_data['description'],
                        'quiz_code': quiz_data['quiz_code'],
                        'order_index': quiz_data['order_index'],
                        'total_questions': len(quiz_data['questions']),
                        'is_active': True
                    }
                    
                    quiz_result = self.client.table('quizzes').insert(quiz_insert_data).execute()
                    quiz_id = quiz_result.data[0]['id']
                    print(f"      Inserted quiz with ID: {quiz_id}")
                    
                    # Insert questions for this quiz
                    for question_data in quiz_data['questions']:
                        question_insert_data = {
                            'quiz_id': quiz_id,
                            'question_text': question_data['question_text'],
                            'option_a': question_data['option_a'],
                            'option_b': question_data['option_b'],
                            'option_c': question_data['option_c'],
                            'option_d': question_data['option_d'],
                            'correct_answer': question_data['correct_answer'],
                            'explanation': question_data['explanation'],
                            'order_index': question_data['order_index']
                        }
                        
                        question_result = self.client.table('questions').insert(question_insert_data).execute()
                        print(f"        Inserted question {question_data['order_index']}")
            
            print("Database seeding completed successfully!")
            
        except Exception as e:
            print(f"Error seeding database: {e}")
            raise
    
    async def run(self, markdown_file_path: str):
        """Run the complete seeding process"""
        print("Starting planets data seeding process...")
        
        # Check if markdown file exists
        if not os.path.exists(markdown_file_path):
            print(f"Error: Markdown file not found at {markdown_file_path}")
            return False
        
        try:
            # Parse the markdown file
            self.parse_quiz_markdown(markdown_file_path)
            
            # Seed the database
            await self.seed_database()
            
            print("Seeding process completed successfully!")
            return True
            
        except Exception as e:
            print(f"Seeding process failed: {e}")
            return False


async def main():
    """Main function to run the seeding process"""
    # Path to the quiz markdown file
    markdown_file_path = "PLANET_QUIZES.md"
    
    # Check if file exists in current directory or parent directory
    if not os.path.exists(markdown_file_path):
        markdown_file_path = "../PLANET_QUIZES.md"
        if not os.path.exists(markdown_file_path):
            print("Error: PLANET_QUIZES.md file not found!")
            print("Please ensure the file exists in the current directory or parent directory.")
            return
    
    # Create seeder instance and run
    seeder = PlanetsDataSeeder()
    success = await seeder.run(markdown_file_path)
    
    if success:
        print("\n✅ Planets and quiz data seeded successfully!")
        print("You can now use the planets API endpoints.")
    else:
        print("\n❌ Seeding failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main()) 