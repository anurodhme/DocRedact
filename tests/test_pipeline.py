import unittest
from src.pii_detector.pii_detector import PIIDetector

class TestPIIDetection(unittest.TestCase):
    def test_email_detection(self):
        detector = PIIDetector()
        text = "Contact me at john.doe@example.com"
        entities = detector.detect_pii(text)
        self.assertTrue(any(entity[1] == 'email' for entity in entities))

if __name__ == '__main__':
    unittest.main()
