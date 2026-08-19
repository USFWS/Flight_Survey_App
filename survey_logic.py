import os
import re
import datetime
import whisper

WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15
}

def parse_count_from_text(text):
    """
    Extracts the wildlife count passively. It prioritizes numbers that 
    are NOT attached to a colony keyword chunk.
    """
    clean_text = text.lower()
    
    # Try to find a standalone number first (like "25 birds")
    # This ignores numbers right next to "colony" or "coliny"
    matches = re.findall(r'\b(\d+)\b', clean_text)
    
    # If we found multiple numbers, check if one is the bird count
    if len(matches) > 1:
        # Look specifically for a number followed by birds, nests, or species words
        bird_match = re.search(r'\b(\d+)\s*(?:birds?|nests?|gulls?|corm|moos|carb|bear|wolf|wolves)?', clean_text)
        if bird_match and not re.search(r'col[o|i]n[y|i|e](?:\s+number)?\s*' + bird_match.group(1), clean_text):
            return bird_match.group(1)
            
    # Standard single digit fallback extraction
    digit_match = re.search(r'\b(\d+)\b', clean_text)
    if digit_match:
        return digit_match.group(1)
        
    for word, num in WORD_TO_NUM.items():
        if re.search(r'\b' + word + r'\b', clean_text):
            return str(num)
    return "1"

def parse_colony_from_text(text):
    """
    Handles background noise typos safely without modifying the raw sentence text.
    Matches: 'colony number 2', 'coliny 2', 'colony number two', etc.
    """
    clean_text = text.lower()
    
    # 1. Look for typo variations followed by digits (e.g., 'coliny number 2' or 'colony 2')
    digit_match = re.search(r'col[o|i]n[y|i|e](?:\s+number)?\s*(\d+)', clean_text)
    if digit_match:
        return digit_match.group(1)
        
    # 2. Look for typo variations followed by text words (e.g., 'coliny number two')
    for word, num in WORD_TO_NUM.items():
        if re.search(r'col[o|i]n[y|i|e](?:\s+number)?\s*' + word, clean_text):
            return str(num)
            
    return None

def get_raw_seconds_string(filename):
    digits = "".join(filter(str.isdigit, filename))
    if len(digits) >= 6:
        try:
            hours = int(digits[0:2])
            minutes = int(digits[2:4])
            seconds = int(digits[4:6])
            if 0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60:
                return str((hours * 3600) + (minutes * 60) + seconds)
        except Exception: pass
    return "0"

def split_transcript_by_species(text, species_dict):
    lower_text = text.lower()
    clauses = re.split(r'\band\b|,|\bplus\b', lower_text)
    clauses = [c.strip() for c in clauses if c.strip()]
    
    matching_codes = []
    for code, description in species_dict.items():
        if description in lower_text or code.lower() in lower_text:
            matching_codes.append((code, description))
            
    if len(matching_codes) <= 1 or len(clauses) <= 1:
        return [text]
        
    detected_phrases = []
    colony_prefix_match = re.search(r'^(col[o|i]n[y|i|e](?:\s+number)?\s*\w+\s*)', lower_text)
    colony_prefix = colony_prefix_match.group(1) if colony_prefix_match else ""

    for clause in clauses:
        for code, description in matching_codes:
            if description in clause or code.lower() in clause:
                final_clause = clause if "col" in clause or not colony_prefix else f"{colony_prefix}{clause}"
                detected_phrases.append(final_clause)
                break
                
    return detected_phrases if detected_phrases else [text]

class SurveyEngine:
    def __init__(self):
        print("Loading Whisper AI 'Base' Model...")
        self.model = whisper.load_model("base")
        print("AI Model Ready!")
        self.species_dict = {}
        self.valid_codes = ["SELECT..."]
        self.ai_vocabulary_prompt = ""

    def load_species_list(self, folder_path):
        species_path = os.path.join(folder_path, "species.csv")
        if not os.path.exists(species_path):
            self.valid_codes = ["NEST", "POOP", "MOOS"]
            return
        try:
            import pandas as pd
            df = pd.read_csv(species_path)
            self.valid_codes = df['Code'].astype(str).tolist()
            self.species_dict = {}
            prompt_words = []
            for _, row in df.iterrows():
                code = str(row['Code'])
                eng = str(row['English_Name']).lower()
                self.species_dict[code] = eng
                prompt_words.extend([row['English_Name'], code])
            self.ai_vocabulary_prompt = "Wildlife survey words: " + ", ".join(prompt_words)
        except Exception as e:
            print(f"Error parsing species file: {str(e)}")
