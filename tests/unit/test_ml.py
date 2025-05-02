"""
Unit tests for the ML components.
"""

import os
import sys
import unittest

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ml import HealthcareTextAnalyzer

class MLTests(unittest.TestCase):
    """Test the ML components."""
    
    def setUp(self):
        """Set up the test case."""
        self.analyzer = HealthcareTextAnalyzer()
        
        # Sample healthcare texts and labels for testing
        self.texts = [
            "Patient presents with chest pain and shortness of breath. History of hypertension.",
            "Routine checkup. No complaints. Blood pressure normal.",
            "Severe abdominal pain. Patient reports nausea and vomiting for 2 days.",
            "Patient has a fever of 101.5F and a cough. Possible flu.",
            "Annual physical examination. Patient is healthy with no significant issues.",
            "Patient complains of joint pain in knees and hips. History of arthritis.",
            "Headache and dizziness for 3 days. No history of migraines.",
            "Patient has elevated blood sugar levels. History of diabetes.",
            "Routine prenatal visit. Fetal heartbeat normal. Mother reports mild nausea.",
            "Patient presents with rash on arms and torso. Itching reported."
        ]
        
        self.labels = [
            "cardiac",
            "routine",
            "gastrointestinal",
            "respiratory",
            "routine",
            "musculoskeletal",
            "neurological",
            "endocrine",
            "obstetric",
            "dermatological"
        ]
    
    def test_01_preprocess_text(self):
        """Test text preprocessing."""
        text = "Patient has a fever of 101.5F and a cough. Possible flu."
        processed = self.analyzer.preprocess_text(text)
        
        # Check that preprocessing removes numbers and special characters
        self.assertNotIn("101.5", processed)
        self.assertNotIn(".", processed)
        
        # Check that preprocessing converts to lowercase
        self.assertNotIn("Patient", processed)
        self.assertIn("patient", processed)
        
        # Check that preprocessing removes stopwords
        self.assertNotIn(" a ", processed)
        self.assertNotIn(" has ", processed)
        self.assertNotIn(" and ", processed)
    
    def test_02_train_model(self):
        """Test model training."""
        self.analyzer.train(self.texts, self.labels)
        
        # Check that the model is trained
        self.assertIsNotNone(self.analyzer.pipeline)
        self.assertIsNotNone(self.analyzer.labels)
        
        # Check that metrics are calculated
        metrics = self.analyzer.get_metrics()
        self.assertIn('accuracy', metrics)
        self.assertIn('classification_report', metrics)
    
    def test_03_predict(self):
        """Test prediction."""
        self.analyzer.train(self.texts, self.labels)
        
        # Test prediction on a new text
        new_text = "Patient reports chest pain radiating to the left arm."
        predictions = self.analyzer.predict([new_text])
        
        # Check that a prediction is made
        self.assertEqual(1, len(predictions))
        self.assertIn(predictions[0], self.labels)
    
    def test_04_predict_proba(self):
        """Test probability prediction."""
        self.analyzer.train(self.texts, self.labels)
        
        # Test probability prediction on a new text
        new_text = "Patient reports chest pain radiating to the left arm."
        probas = self.analyzer.predict_proba([new_text])
        
        # Check that probabilities are calculated
        self.assertEqual(1, len(probas))
        self.assertIsInstance(probas[0], dict)
        
        # Check that probabilities sum to approximately 1
        total_proba = sum(probas[0].values())
        self.assertAlmostEqual(1.0, total_proba, places=1)
    
    def test_05_extract_keywords(self):
        """Test keyword extraction."""
        self.analyzer.train(self.texts, self.labels)
        
        # Test keyword extraction on a text
        text = "Patient presents with chest pain and shortness of breath. History of hypertension."
        keywords = self.analyzer.extract_keywords(text, top_n=5)
        
        # Check that keywords are extracted
        self.assertLessEqual(len(keywords), 5)
        self.assertIsInstance(keywords[0], tuple)
        self.assertEqual(2, len(keywords[0]))  # (keyword, score)

if __name__ == "__main__":
    unittest.main()
