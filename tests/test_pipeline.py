import sys
import os
import unittest

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pii_detector.pii_detector import PIIDetector

class TestPIIDetection(unittest.TestCase):
    def test_email_detection(self):
        """Test that email addresses are correctly detected"""
        detector = PIIDetector()
        text = "Please contact john.doe@example.com for more information."
        entities = detector.detect_pii(text)
        
        # Check that we found the email
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0][0], "john.doe@example.com")
        self.assertEqual(entities[0][1], "email")

if __name__ == '__main__':
    unittest.main()
