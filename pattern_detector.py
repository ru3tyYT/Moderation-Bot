# pattern_detector.py - Advanced slur detection with pattern matching
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
            'a': ['a', '4', '@', 'α', 'а'],
            'e': ['e', '3', 'ε', 'е'],
            'i': ['i', '1', '!', 'l', '|', 'ı', 'і'],
            'o': ['o', '0', 'ο', 'о'],
            'u': ['u', 'v', 'υ', 'у'],
            's': ['s', '5', '$', 'ş', 'ѕ'],
            'g': ['g', '9', 'q'],
            'z': ['z', '2'],
            'b': ['b', '8'],
            't': ['t', '7', '+'],
            'c': ['c', '(', '<', 'с'],
            'k': ['k', 'х'],
            'n': ['n', 'η', 'п'],
            'r': ['r', 'г'],
            'h': ['h', 'н'],
            'x': ['x', 'х'],
            'p': ['p', 'р'],
            'y': ['y', 'у'],
            'w': ['w', 'vv', 'ω'],
            'm': ['m', 'rn'],
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
            else:
                pattern_parts.append(re.escape(char))
        
        # Join with optional spaces, dots, dashes, underscores
        pattern = '[\\s._-]*'.join(pattern_parts)
        
        # Word boundary or non-letter on both sides
        full_pattern = f'(?:^|\\W)({pattern})(?:$|\\W)'
        
        return full_pattern
    
    def check_text(self, text: str, pattern_list: List[str]) -> Tuple[bool, List[str]]:
        """
        Check text against pattern list.
        Returns: (found, list_of_matches)
        """
        text_lower = text.lower()
        found_matches = []
        
        for pattern in pattern_list:
            regex = self.create_pattern(pattern)
            matches = re.finditer(regex, text_lower, re.IGNORECASE)
            
            for match in matches:
                found_matches.append(match.group(1))
        
        return len(found_matches) > 0, found_matches
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by replacing common substitutions.
        Useful for additional checking.
        """
        normalized = text.lower()
        
        # Replace common substitutions
        replacements = {
            '4': 'a', '@': 'a',
            '3': 'e',
            '1': 'i', '!': 'i', '|': 'i',
            '0': 'o',
            '5': 's', '$': 's',
            '7': 't',
            '8': 'b',
            '9': 'g',
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove spaces, dots, dashes between letters
        normalized = re.sub(r'([a-z])[\\s._-]+([a-z])', r'\\1\\2', normalized)
        
        return normalized


# Example usage in bot
def enhanced_slur_check(text: str) -> Tuple[bool, List[str]]:
    """
    Enhanced slur detection using pattern matching.
    Add your base words here (use first 2-3 letters only for reference).
    """
    detector = PatternDetector()
    
    # Base patterns - just reference prefixes, not full words
    # The actual detection happens through pattern matching
    base_patterns = [
        # You would add base patterns here
        # Example format (not actual slurs):
        # "n*g", "f*g", "k*k", etc.
        # The asterisks would be removed and pattern matching applied
    ]
    
    # Check original text
    found, matches = detector.check_text(text, base_patterns)
    
    if found:
        return True, matches
    
    # Check normalized text (catches more variations)
    normalized = detector.normalize_text(text)
    found_norm, matches_norm = detector.check_text(normalized, base_patterns)
    
    return found_norm, matches_norm


# Integration with bot.py
def contains_slur_advanced(text: str) -> Tuple[bool, List[str]]:
    """
    Advanced slur detection that catches:
    - Leetspeak: n1gger, f4ggot
    - Spacing: n i g g e r
    - Mixed: n 1 g g 3 r
    - Unicode: using Cyrillic/Greek letters
    - Dots/dashes: n.i.g.g.e.r, n-i-g-g-e-r
    """
    return enhanced_slur_check(text)
