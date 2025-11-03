# pattern_detector.py - Advanced Pattern Matching Engine
import re
from typing import List, Tuple

class PatternDetector:
    """
    Advanced pattern-based detection that catches variations without listing explicit words.
    Catches: leetspeak, spacing, unicode substitution, homoglyphs, etc.
    """
    
    def __init__(self):
        # Character substitution mappings for leetspeak/bypass attempts
        self.substitutions = {
            'a': ['a', '4', '@', 'α', 'а', 'A'],
            'e': ['e', '3', 'ε', 'е', 'E'],
            'i': ['i', '1', '!', 'l', '|', 'ı', 'і', 'I'],
            'o': ['o', '0', 'ο', 'о', 'O'],
            'u': ['u', 'v', 'υ', 'у', 'U'],
            's': ['s', '5', '$', 'ş', 'ѕ', 'S'],
            'g': ['g', '9', 'q', 'G'],
            'z': ['z', '2', 'Z'],
            'b': ['b', '8', 'B'],
            't': ['t', '7', '+', 'T'],
            'c': ['c', '(', '<', 'с', 'C'],
            'k': ['k', 'х', 'K'],
            'n': ['n', 'η', 'п', 'N'],
            'r': ['r', 'г', 'R'],
            'h': ['h', 'н', 'H'],
            'x': ['x', 'х', 'X'],
            'p': ['p', 'р', 'P'],
            'y': ['y', 'у', 'Y'],
            'w': ['w', 'vv', 'ω', 'W'],
            'm': ['m', 'rn', 'M'],
            'd': ['d', 'D'],
            'f': ['f', 'F'],
            'j': ['j', 'J'],
            'l': ['l', '1', 'L'],
            'q': ['q', 'Q'],
            'v': ['v', 'V'],
        }
    
    def create_pattern(self, base_word: str) -> str:
        """
        Creates a regex pattern that matches variations of a word.
        Catches leetspeak, spacing, unicode substitution, etc.
        """
        pattern_parts = []
        
        for char in base_word.lower():
            if char in self.substitutions:
                # Create character class with all substitutions
                char_class = ''.join(self.substitutions[char])
                pattern_parts.append(f'[{re.escape(char_class)}]')
            elif char == ' ':
                # Space can be space, underscore, dash, dot, or nothing
                pattern_parts.append('[\\s._-]*')
            else:
                pattern_parts.append(re.escape(char))
        
        # Join with optional spaces, dots, dashes, underscores between characters
        pattern = '[\\s._-]*'.join(pattern_parts)
        
        # Word boundary or non-letter on both sides
        full_pattern = f'(?:^|\\W)({pattern})(?:$|\\W)'
        
        return full_pattern
    
    def check_text(self, text: str, pattern_list: List[str]) -> Tuple[bool, List[str]]:
        """
        Check text against pattern list.
        Returns: (found, list_of_matches)
        """
        if not text or not pattern_list:
            return False, []
        
        text_lower = text.lower()
        found_matches = []
        
        for pattern in pattern_list:
            try:
                regex = self.create_pattern(pattern)
                matches = re.finditer(regex, text_lower, re.IGNORECASE)
                
                for match in matches:
                    matched_text = match.group(1)
                    if matched_text and matched_text not in found_matches:
                        found_matches.append(matched_text)
            except Exception as e:
                print(f"Error checking pattern '{pattern}': {e}")
                continue
        
        return len(found_matches) > 0, found_matches
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by replacing common substitutions.
        Useful for additional checking.
        """
        if not text:
            return ""
        
        normalized = text.lower()
        
        # Replace common substitutions
        replacements = {
            '4': 'a', '@': 'a',
            '3': 'e',
            '1': 'i', '!': 'i', '|': 'i',
            '0': 'o',
            '5': 's', '$': 's',
            '7': 't', '+': 't',
            '8': 'b',
            '9': 'g',
            '2': 'z',
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove spaces, dots, dashes, underscores between letters
        normalized = re.sub(r'([a-z])[\s._-]+([a-z])', r'\1\2', normalized)
        
        return normalized
