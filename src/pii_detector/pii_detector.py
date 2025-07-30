import spacy
import re
from typing import List, Tuple

class PIIDetector:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            self.nlp = None
        
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b'
        }
    
    def detect_pii(self, text: str) -> List[Tuple[str, str, int, int]]:
        """Detect PII entities in text"""
        pii_entities = []
        
        # spaCy NER detection
        if self.nlp is not None:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "GPE"]:
                    pii_entities.append((ent.text, ent.label_.lower(), ent.start_char, ent.end_char))
        
        # Regex pattern matching
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                pii_entities.append((match.group(), pii_type, match.start(), match.end()))
        
        return pii_entities
