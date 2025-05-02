"""
Unit tests for model validation framework.
Tests both base ModelValidator and healthcare-specific validator.
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime
from src.ml.model_validator import ModelValidator
from src.ml.healthcare_validator import HealthcareModelValidator

class TestModelValidation(unittest.TestCase):
    """Test cases for model validation framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_validator = ModelValidator("test_model", "1.0.0")
        self.healthcare_validator = HealthcareModelValidator("healthcare_model", "1.0.0")
        
        # Create sample test data
        np.random.seed(42)
        self.sample_size = 1000
        
        # Generate synthetic predictions and ground truth
        self.y_true = np.random.randint(0, 2, self.sample_size)
        self.y_pred = np.random.randint(0, 2, self.sample_size)
        self.y_prob = np.random.random(self.sample_size)
        
        # Generate healthcare-specific test data
        self.age_predictions = np.random.normal(45, 15, self.sample_size)  # Age predictions
        self.bmi_predictions = np.random.normal(25, 5, self.sample_size)   # BMI predictions
        self.cost_predictions = np.random.normal(13000, 5000, self.sample_size)  # Cost predictions
        
        # Create sample sensitive features
        self.sensitive_features = pd.DataFrame({
            'age_group': np.random.choice(['18-30', '31-50', '51+'], self.sample_size),
            'sex': np.random.choice(['F', 'M'], self.sample_size),
            'race': np.random.choice(['A', 'B', 'C'], self.sample_size),
            'region': np.random.choice(['NE', 'NW', 'SE', 'SW'], self.sample_size)
        })
    
    def test_base_performance_validation(self):
        """Test basic model performance validation."""
        metrics = self.base_validator.validate_performance(
            self.y_true,
            self.y_pred,
            self.y_prob
        )
        
        # Check that all expected metrics are present
        expected_metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'confusion_matrix']
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
            
        # Check metric values are in valid ranges
        self.assertGreaterEqual(metrics['accuracy'], 0)
        self.assertLessEqual(metrics['accuracy'], 1)
        self.assertGreaterEqual(metrics['roc_auc'], 0)
        self.assertLessEqual(metrics['roc_auc'], 1)
    
    def test_base_output_validation(self):
        """Test model output validation."""
        validation_results = self.base_validator.validate_outputs(
            self.cost_predictions,
            expected_range=(0, 50000),
            validation_rules=[{
                "type": "range",
                "name": "cost_range",
                "range": (0, 50000)
            }]
        )
        
        self.assertIn('total_outputs', validation_results)
        self.assertIn('checks', validation_results)
        self.assertIn('statistics', validation_results)
    
    def test_base_bias_analysis(self):
        """Test basic bias analysis."""
        bias_results = self.base_validator.analyze_bias(
            self.y_pred,
            self.sensitive_features,
            self.y_true
        )
        
        self.assertIn('metrics', bias_results)
        self.assertIn('group_disparities', bias_results)
    
    def test_healthcare_output_validation(self):
        """Test healthcare-specific output validation."""
        # Test age predictions
        age_results = self.healthcare_validator.validate_healthcare_outputs(
            self.age_predictions,
            output_type='age_distribution'
        )
        self.assertIn('healthcare_specific_checks', age_results)
        
        # Test BMI predictions
        bmi_results = self.healthcare_validator.validate_healthcare_outputs(
            self.bmi_predictions,
            output_type='bmi_distribution'
        )
        self.assertIn('healthcare_specific_checks', bmi_results)
        
        # Test cost predictions
        cost_results = self.healthcare_validator.validate_healthcare_outputs(
            self.cost_predictions,
            output_type='cost_distribution',
            metadata={'clinical_context': {'setting': 'emergency'}}
        )
        self.assertIn('healthcare_specific_checks', cost_results)
        self.assertIn('clinical_validity', cost_results)
    
    def test_healthcare_bias_analysis(self):
        """Test healthcare-specific bias analysis."""
        bias_results = self.healthcare_validator.analyze_healthcare_bias(
            self.cost_predictions,
            self.sensitive_features,
            self.y_true
        )
        
        self.assertIn('protected_attributes', bias_results)
        self.assertIn('healthcare_disparities', bias_results)
        self.assertIn('compliance_status', bias_results)
    
    def test_regulatory_compliance(self):
        """Test regulatory compliance checks."""
        # First run performance validation to populate metrics
        self.healthcare_validator.validate_performance(
            self.y_true,
            self.y_pred,
            self.y_prob
        )
        
        # Then test compliance checks
        results = self.healthcare_validator._check_regulatory_compliance(
            self.cost_predictions,
            metadata={'clinical_context': {'setting': 'standard'}}
        )
        
        self.assertIn('compliant', results)
        self.assertIn('checks', results)
    
    def test_clinical_validity(self):
        """Test clinical validity checks."""
        results = self.healthcare_validator._check_clinical_validity(
            self.cost_predictions,
            output_type='cost',
            metadata={'clinical_context': {'setting': 'emergency'}}
        )
        
        self.assertIn('clinically_valid', results)
        self.assertIn('warnings', results)
    
    def test_version_comparison(self):
        """Test model version comparison."""
        # Create results for two versions
        v1_results = self.healthcare_validator.validation_results
        
        v2_validator = HealthcareModelValidator("healthcare_model", "2.0.0")
        v2_validator.validate_performance(self.y_true, self.y_pred, self.y_prob)
        v2_results = v2_validator.validation_results
        
        # Compare versions
        comparison = self.healthcare_validator.compare_versions(v2_results)
        
        self.assertIn('metric_deltas', comparison)
        self.assertIn('significant_changes', comparison)
    
    def test_error_handling(self):
        """Test error handling in validators."""
        # Test with invalid inputs
        with self.assertRaises(Exception):
            self.base_validator.validate_performance(
                np.array([]),  # Empty array
                np.array([]),
                np.array([])
            )
        
        with self.assertRaises(Exception):
            self.healthcare_validator.validate_healthcare_outputs(
                np.array([]),  # Empty array
                output_type='invalid_type'
            )
    
    def test_result_saving(self):
        """Test saving validation results."""
        # Run some validations
        self.healthcare_validator.validate_performance(
            self.y_true,
            self.y_pred,
            self.y_prob
        )
        
        # Save results
        output_path = self.healthcare_validator.save_results("test_results")
        
        self.assertTrue(output_path.endswith('.json'))
        # In a real test, would also check file exists and content is valid

if __name__ == '__main__':
    unittest.main()