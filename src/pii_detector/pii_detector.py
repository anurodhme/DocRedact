# src/pii_detector/pii_detector.py

"""
PII Detector Module

Detects Personally Identifiable Information (PII) in text using:
- spaCy for Named Entity Recognition (NER): detects PERSON, ORG, GPE
- Regular expressions for structured PII: email, phone, credit card

Returns entities with their type and character span for redaction purposes.
"""

import spacy
import re
from typing import List, Tuple


class PIIDetector:
    """
    A robust PII detection class that combines spaCy's NLP capabilities
    with regex pattern matching to identify sensitive information in text.
    """

    def __init__(self):
        """
        Initialize the detector by loading the spaCy English model.
        Raises a clear error if the model is not installed.
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise OSError(
                "SpaCy model 'en_core_web_sm' not found. "
                "Please install it using: python -m spacy download en_core_web_sm"
            )
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading spaCy model: {e}")

        # Define regex patterns for structured PII
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b'
        }

    def detect_pii(self, text: str) -> List[Tuple[str, str, int, int]]:
        """
        Detect PII entities in the input text.

        Args:
            text (str): Input text to scan for PII.

        Returns:
            List[Tuple[str, str, int, int]]: List of tuples containing
                (entity_text, entity_type, start_index, end_index)
                Example: ('john@example.com', 'email', 10, 30)
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        pii_entities = []

        # 1. Use spaCy for NER (PERSON, ORG, GPE)
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE"]:
                pii_entities.append((ent.text, ent.label_.lower(), ent.start_char, ent.end_char))

        # 2. Regex-based detection for structured PII
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                pii_entities.append((match.group(), pii_type, match.start(), match.end()))

        # Sort entities by start index for consistent output
        pii_entities.sort(key=lambda x: x[2])

        return pii_entities

    def redact(self, text: str, mask: str = "[REDACTED]") -> str:
        """
        Redact detected PII from the input text.

        Args:
            text (str): Input text to redact.
            mask (str): Replacement string (default: [REDACTED]).

        Returns:
            str: Redacted text with PII replaced by mask.
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        entities = self.detect_pii(text)
        # Sort by end index in reverse to avoid shifting issues during replacement
        for _, _, start, end in sorted(entities, key=lambda x: x[3], reverse=True):
            text = text[:start] + mask + text[end:]
        return text