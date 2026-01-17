# pattern_detector.py - Advanced Pattern Matching Engine
import re
from typing import List, Tuple

class PatternDetector:
    """
    Advanced pattern-based detection that catches variations without listing explicit words.
    Catches: leetspeak, spacing, unicode substitution, homoglyphs, number substitutions, etc.
    """

    def __init__(self):
        self.substitutions = {
            'a': ['a', '4', '@', 'α', 'а', 'A', 'ä', 'ȧ', 'ạ', 'ả', 'ầ', 'ấ', 'ậ', 'ẩ', 'ẫ', 'ā', 'ă', 'ą'],
            'e': ['e', '3', 'ε', 'е', 'E', 'è', 'é', 'ê', 'ẻ', 'ể', 'ệ', 'ę', 'ė', 'ē', 'ě', 'є'],
            'i': ['i', '1', '!', 'l', '|', 'ı', 'і', 'I', 'ì', 'í', 'î', 'ị', 'ỉ', 'ī', 'ĭ', 'ı'],
            'o': ['o', '0', 'ο', 'о', 'O', 'ö', 'ø', 'ọ', 'ỏ', 'ố', 'ộ', 'ồ', 'ố', 'ō', 'ŏ', 'õ'],
            'u': ['u', 'v', 'υ', 'у', 'U', 'ü', 'ú', 'ù', 'ụ', 'ủ', 'ứ', 'ữ', 'ự', 'ū', 'ŭ', 'ů'],
            's': ['s', '5', '$', 'ş', 'ѕ', 'S', 'ś', 'š', 'ṣ', 'ș'],
            'g': ['g', '9', 'q', 'G', 'ġ', 'ĝ', 'ğ', 'g̃', 'g̈'],
            'z': ['z', '2', 'Z', 'ż', 'ž', 'ź'],
            'b': ['b', '8', 'B', 'ƀ', 'ḅ', 'ƃ'],
            't': ['t', '7', '+', 'T', 'τ', 'т', 'ŧ', 'ẗ', 'ṭ', 'ț'],
            'c': ['c', '(', '<', 'с', 'C', 'ċ', 'č', 'ḉ', 'ç'],
            'k': ['k', 'х', 'K', 'κ', 'ķ', 'ǩ', 'ḵ'],
            'n': ['n', 'η', 'п', 'N', 'ñ', 'ń', 'ň', 'ṇ', 'ņ'],
            'r': ['r', 'г', 'R', 'ŕ', 'ř', 'ṛ', 'ŗ'],
            'h': ['h', 'н', 'H', 'ħ', 'ḥ', 'ẖ'],
            'x': ['x', 'х', 'X', 'χ', 'ẋ', 'ẍ'],
            'p': ['p', 'р', 'P', 'ṗ', 'ṕ', 'ƥ'],
            'y': ['y', 'у', 'Y', 'ý', 'ÿ', 'ẏ', 'ȳ', 'ỵ'],
            'w': ['w', 'vv', 'ω', 'W', 'ŵ', 'ẁ', 'ẃ', 'ẅ', 'ẇ'],
            'm': ['m', 'rn', 'M', 'ṁ', 'ṃ', 'ɱ'],
            'd': ['d', 'D', 'ḍ', 'ḑ', 'đ', 'ď'],
            'f': ['f', 'F', 'ḟ', 'ƒ'],
            'j': ['j', 'J', 'ĵ', 'ǰ', 'ɉ'],
            'l': ['l', '1', 'L', 'ł', 'ĺ', 'ľ', 'ḷ', 'ₗ'],
            'q': ['q', 'Q', 'ġ', 'ʠ'],
            'v': ['v', 'V', 'ṽ', 'ṿ', 'ⅴ'],
        }

        self.spacing_patterns = [
            (r'\s+', ''),
            (r'(\w)\s+(\w)', r'\1\2'),
            (r'(\w)[._-]+(\w)', r'\1\2'),
        ]

    def create_pattern(self, base_word: str) -> str:
        """
        Creates a regex pattern that matches variations of a word.
        Catches leetspeak, spacing, unicode substitution, etc.
        """
        pattern_parts = []

        for char in base_word.lower():
            if char in self.substitutions:
                char_class = ''.join(self.substitutions[char])
                pattern_parts.append(f'[{re.escape(char_class)}]')
            elif char == ' ':
                pattern_parts.append('[\\s._-]*')
            else:
                pattern_parts.append(re.escape(char))

        pattern = '[\\s._-]*'.join(pattern_parts)
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

        normalized = self.normalize_text(text)
        if normalized != text_lower:
            for pattern in pattern_list:
                try:
                    regex = self.create_pattern(pattern)
                    matches = re.finditer(regex, normalized, re.IGNORECASE)

                    for match in matches:
                        matched_text = match.group(1)
                        if matched_text and matched_text not in found_matches:
                            found_matches.append(matched_text)
                except Exception as e:
                    continue

        return len(found_matches) > 0, found_matches

    def normalize_text(self, text: str) -> str:
        """
        Normalize text by replacing common substitutions.
        """
        if not text:
            return ""

        normalized = text.lower()

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

        normalized = re.sub(r'([a-z])[\s._-]+([a-z])', r'\1\2', normalized)

        return normalized
