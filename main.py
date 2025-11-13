import csv
import random
import sys
import os
from pathlib import Path

class TestMaker:
    def __init__(self, csv_file):
        self.terms_definitions = self.load_csv(csv_file)
        if not self.terms_definitions:
            print("Error: No data loaded from CSV file.")
            sys.exit(1)
        
    def load_csv(self, csv_file):
        """Load terms and definitions from CSV file"""
        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 2:
                        term = row[0].strip()
                        definition = row[1].strip()
                        if term and definition:  # Skip empty rows
                            data.append({'term': term, 'definition': definition})
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file}' not found.")
            return []
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []
        return data
    
    def get_user_preferences(self):
        """Get user preferences for the test"""
        print("=== Test Maker ===")
        print(f"Total terms available: {len(self.terms_definitions)}")
        
        # Validate that we have enough terms for the requested questions
        max_possible = len(self.terms_definitions)
        
        while True:
            try:
                print("\n--- Question Type Settings ---")
                
                # Definition questions (pick correct definition from options)
                def_questions = int(input("How many 'pick correct definition' questions? "))
                if def_questions < 0:
                    print("Please enter a non-negative number.")
                    continue
                if def_questions > max_possible:
                    print(f"Only {max_possible} questions possible with current data.")
                    continue
                    
                def_choices = 4  # Default
                if def_questions > 0:
                    def_choices = int(input("How many choices for definition questions? "))
                    if def_choices < 2 or def_choices > max_possible:
                        print(f"Choices must be between 2 and {max_possible}.")
                        continue
                
                # Term questions (pick correct term from options)
                term_questions = int(input("How many 'pick correct term' questions? "))
                if term_questions < 0:
                    print("Please enter a non-negative number.")
                    continue
                if term_questions > max_possible:
                    print(f"Only {max_possible} questions possible with current data.")
                    continue
                    
                term_choices = 4  # Default
                if term_questions > 0:
                    term_choices = int(input("How many choices for term questions? "))
                    if term_choices < 2 or term_choices > max_possible:
                        print(f"Choices must be between 2 and {max_possible}.")
                        continue
                
                # True/False questions
                tf_questions = int(input("How many True/False questions? "))
                if tf_questions < 0:
                    print("Please enter a non-negative number.")
                    continue
                if tf_questions > max_possible:
                    print(f"Only {max_possible} questions possible with current data.")
                    continue
                
                total_questions = def_questions + term_questions + tf_questions
                if total_questions == 0:
                    print("You must create at least one question!")
                    continue
                    
                if total_questions > len(self.terms_definitions):
                    print(f"Warning: You're requesting {total_questions} questions but only have {len(self.terms_definitions)} terms.")
                    continue
                    
                return {
                    'def_questions': def_questions,
                    'def_choices': def_choices,
                    'term_questions': term_questions,
                    'term_choices': term_choices,
                    'tf_questions': tf_questions
                }
                
            except ValueError:
                print("Please enter valid numbers.")
    
    def generate_definition_question(self, used_indices, num_choices):
        """Generate a 'pick correct definition' question"""
        # Find available indices (not used yet)
        available_indices = [i for i in range(len(self.terms_definitions)) if i not in used_indices]
        
        if len(available_indices) < num_choices:
            return None, None, None
        
        # Select correct answer
        correct_idx = random.choice(available_indices)
        correct_item = self.terms_definitions[correct_idx]
        used_indices.add(correct_idx)
        
        # Select distractors
        distractor_indices = random.sample(
            [i for i in available_indices if i != correct_idx], 
            num_choices - 1
        )
        distractors = [self.terms_definitions[i]['definition'] for i in distractor_indices]
        
        # Combine and shuffle options
        options = [correct_item['definition']] + distractors
        random.shuffle(options)
        
        correct_num = str(options.index(correct_item['definition'])+1)
        
        question = f"What is the definition of '{correct_item['term']}'?"
        
        return question, options, correct_num
    
    def generate_term_question(self, used_indices, num_choices):
        """Generate a 'pick correct term' question"""
        available_indices = [i for i in range(len(self.terms_definitions)) if i not in used_indices]
        
        if len(available_indices) < num_choices:
            return None, None, None
        
        # Select correct answer
        correct_idx = random.choice(available_indices)
        correct_item = self.terms_definitions[correct_idx]
        used_indices.add(correct_idx)
        
        # Select distractors
        distractor_indices = random.sample(
            [i for i in available_indices if i != correct_idx], 
            num_choices - 1
        )
        distractors = [self.terms_definitions[i]['term'] for i in distractor_indices]
        
        # Combine and shuffle options
        options = [correct_item['term']] + distractors
        random.shuffle(options)
        
        correct_num = str(options.index(correct_item['term'])+1)
        
        question = f"Which term matches this definition: '{correct_item['definition']}'?"
        
        return question, options, correct_num
    
    def generate_tf_question(self, used_indices):
        """Generate a True/False question"""
        available_indices = [i for i in range(len(self.terms_definitions)) if i not in used_indices]
        
        if not available_indices:
            return None, None, None
        
        # For True questions: use correct term-definition pairs
        # For False questions: mix terms with wrong definitions
        is_true = random.choice([True, False])
        
        correct_idx = random.choice(available_indices)
        correct_item = self.terms_definitions[correct_idx]
        used_indices.add(correct_idx)
        
        if is_true:
            question = f"True or False: The term '{correct_item['term']}' means '{correct_item['definition']}'"
            correct_answer = "1"
            options = ['True', 'False']
        else:
            # Find a different definition
            wrong_idx = random.choice([i for i in available_indices if i != correct_idx])
            wrong_definition = self.terms_definitions[wrong_idx]['definition']
            
            question = f"True or False: The term '{correct_item['term']}' means '{wrong_definition}'"
            correct_answer = "2"
            options = ['True', 'False']
        
        return question, options, correct_answer
    
    def display_question(self, question_number, question, options):
        """Display a question and get user's answer"""
        print(f"\n--- Question {question_number} ---")
        print(question)
        print("\nOptions:")
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        
        while True:
            answer = input("\nYour answer (enter 1, 2, 3, etc.): ").upper().strip()
            if answer and answer in [str(i+1) for i in range(len(options))]:
                return answer
            else:
                print(f"Please enter a valid choice (1-{len(options) - 1})")
    
    def run_test(self):
        """Run the complete test"""
        preferences = self.get_user_preferences()
        
        print(f"\n=== Starting Test ===")
        print(f"Total questions: {sum(list(preferences.values())[::2])}")
        
        score = 0
        total_questions = 0
        used_indices = set()
        question_number = 1
        
        # Generate definition questions
        for _ in range(preferences['def_questions']):
            question, options, correct_answer = self.generate_definition_question(
                used_indices, preferences['def_choices']
            )
            if question is None:
                print("Not enough terms for all definition questions.")
                break
                
            user_answer = self.display_question(question_number, question, options)
            if user_answer == correct_answer:
                print("✓ Correct!")
                score += 1
            else:
                print(f"✗ Incorrect. The correct answer was {correct_answer}.")
            total_questions += 1
            question_number += 1
        
        # Generate term questions
        for _ in range(preferences['term_questions']):
            question, options, correct_answer = self.generate_term_question(
                used_indices, preferences['term_choices']
            )
            if question is None:
                print("Not enough terms for all term questions.")
                break
                
            user_answer = self.display_question(question_number, question, options)
            if user_answer == correct_answer:
                print("✓ Correct!")
                score += 1
            else:
                print(f"✗ Incorrect. The correct answer was {correct_answer}.")
            total_questions += 1
            question_number += 1
        
        # Generate True/False questions
        for _ in range(preferences['tf_questions']):
            question, options, correct_answer = self.generate_tf_question(used_indices)
            if question is None:
                print("Not enough terms for all True/False questions.")
                break
                
            user_answer = self.display_question(question_number, question, options)
            if user_answer == correct_answer:
                print("✓ Correct!")
                score += 1
            else:
                print(f"✗ Incorrect. The correct answer was {correct_answer}.")
            total_questions += 1
            question_number += 1
        
        # Display final results
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        print(f"\n=== Test Results ===")
        print(f"Score: {score}/{total_questions} ({percentage:.1f}%)")
        
        if percentage >= 90:
            print("Excellent work! 🎉")
        elif percentage >= 80:
            print("Great job! 👍")
        elif percentage >= 70:
            print("Good work! 👏")
        elif percentage >= 60:
            print("You passed! ✅")
        else:
            print("Keep practicing! 📚")

def get_csv_files():
    """Get all CSV files from the data folder"""
    data_folder = Path("data")
    
    # Create data folder if it doesn't exist
    if not data_folder.exists():
        data_folder.mkdir()
        print("Created 'data' folder. Please add your CSV files there.")
        return []
    
    csv_files = list(data_folder.glob("*.csv"))
    
    return sorted(csv_files)

def select_csv_file():
    """Let user select a CSV file from the data folder"""
    csv_files = get_csv_files()
    
    if not csv_files:
        print("No CSV files found in the 'data' folder.")
        print("Please add CSV files with the following format:")
        print("term1,definition1")
        print("term2,definition2")
        print("...")
        sys.exit(1)
    
    print("Available CSV files in 'data' folder:")
    print("-" * 40)
    
    for i, csv_file in enumerate(csv_files, 1):
        # Count terms in the CSV file
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                term_count = sum(1 for row in reader if len(row) >= 2 and row[0].strip() and row[1].strip())
        except:
            term_count = 0
        
        print(f"{i}. {csv_file.name} ({term_count} terms)")
    
    print("-" * 40)
    
    while True:
        try:
            choice = int(input(f"Select a file (1-{len(csv_files)}): "))
            if 1 <= choice <= len(csv_files):
                return str(csv_files[choice - 1])
            else:
                print(f"Please enter a number between 1 and {len(csv_files)}.")
        except ValueError:
            print("Please enter a valid number.")



def main():
    print("Welcome to the Test Maker!")
    print("=" * 50)
    
    # Let user select a CSV file from the data folder
    csv_file = select_csv_file()
    
    print(f"\nSelected: {os.path.basename(csv_file)}")   
    # Create test maker and run test
    test_maker = TestMaker(csv_file)
    test_maker.run_test()

if __name__ == "__main__":
    main()
