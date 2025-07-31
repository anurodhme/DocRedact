# src/pii_detector/pii_detector.py
import spacy
import re
from typing import List, Tuple


class PIIDetector:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise OSError(
                "SpaCy model 'en_core_web_sm' not found. "
                "Please install it with: python -m spacy download en_core_web_sm"
            )
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading spaCy model: {e}")

        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            'phone': r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b'
        }

    def detect_pii(self, text: str) -> List[Tuple[str, str, int, int]]:
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        pii_entities = []

        # NER via spaCy
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE"]:
                pii_entities.append((ent.text, ent.label_.lower(), ent.start_char, ent.end_char))

        # Regex matching
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                pii_entities.append((match.group(), pii_type, match.start(), match.end()))

        pii_entities.sort(key=lambda x: x[2])  # Sort by start index
        return pii_entities

    def redact(self, text: str, mask: str = "[REDACTED]") -> str:
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        entities = self.detect_pii(text)
        for _, _, start, end in sorted(entities, key=lambda x: x[3], reverse=True):
            text = text[:start] + mask + text[end:]
        return text