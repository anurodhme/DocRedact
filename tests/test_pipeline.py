# tests/test_pipeline.py

import sys
import os
import unittest

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pii_detector.pii_detector import PIIDetector


class TestPIIDetection(unittest.TestCase):
    """Test suite for PIIDetector PII detection functionality."""

    def setUp(self):
        """Set up detector instance before each test."""
        self.detector = PIIDetector()

    def test_email_detection(self):
        """Test that email addresses are correctly detected."""
        text = "Please contact john.doe@example.com for more information."
        entities = self.detector.detect_pii(text)

        # Check that the email is detected (allow flexible span)
        email_found = any(
            e[0] == "john.doe@example.com" and e[1] == "email"
            for e in entities
        )
        self.assertTrue(email_found, "Email address not detected")

    def test_phone_detection(self):
        """Test that phone numbers are correctly detected."""
        text = "Call me at (555) 123-4567 or +1-800-999-8888."
        entities = self.detector.detect_pii(text)

        # Check presence without strict span matching
        phone1_found = any(e[0] == "(555) 123-4567" and e[1] == "phone" for e in entities)
        phone2_found = any(e[0] == "+1-800-999-8888" and e[1] == "phone" for e in entities)

        self.assertTrue(phone1_found, "Phone number '(555) 123-4567' not detected")
        self.assertTrue(phone2_found, "Phone number '+1-800-999-8888' not detected")

    def test_credit_card_detection(self):
        """Test that credit card numbers are detected."""
        text = "My card is 4111-1111-1111-1111 or 5500000000000004."
        entities = self.detector.detect_pii(text)

        cc1_found = any(e[0] == "4111-1111-1111-1111" and e[1] == "credit_card" for e in entities)
        cc2_found = any(e[0] == "5500000000000004" and e[1] == "credit_card" for e in entities)

        self.assertTrue(cc1_found, "Credit card '4111-...' not detected")
        self.assertTrue(cc2_found, "Credit card '550000...' not detected")

    def test_person_detection(self):
        """Test that PERSON entities are detected via spaCy."""
        text = "Hello, my name is Alice Johnson."
        entities = self.detector.detect_pii(text)

        person_found = any("Alice Johnson" in e[0] and e[1] == "person" for e in entities)
        self.assertTrue(person_found, "Person name 'Alice Johnson' not detected")

    def test_mixed_pii_detection(self):
        """Test detection of multiple PII types in one text."""
        text = """
        John Smith lives at 123 Main St, New York.
        Contact: john.smith@email.com | Phone: (212) 555-1234.
        Card: 4000-1234-5678-9012.
        """
        entities = self.detector.detect_pii(text)

        self.assertTrue(any(e[0] == "john.smith@email.com" and e[1] == "email" for e in entities))
        self.assertTrue(any(e[0] == "(212) 555-1234" and e[1] == "phone" for e in entities))
        self.assertTrue(any(e[0] == "4000-1234-5678-9012" and e[1] == "credit_card" for e in entities))
        self.assertTrue(any("John Smith" in e[0] and e[1] == "person" for e in entities))
        self.assertTrue(any("New York" in e[0] and e[1] == "gpe" for e in entities))

    def test_empty_text(self):
        """Test behavior on empty string."""
        entities = self.detector.detect_pii("")
        self.assertEqual(entities, [])

    def test_non_string_input(self):
        """Test that non-string input raises an error."""
        with self.assertRaises(ValueError):
            self.detector.detect_pii(None)
        with self.assertRaises(ValueError):
            self.detector.detect_pii(123)


if __name__ == '__main__':
    unittest.main()