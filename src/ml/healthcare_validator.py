"""
Healthcare-specific model validation framework.

This module extends the base ModelValidator with healthcare-specific:
1. Domain validation rules
2. Healthcare metrics
3. Fairness considerations
4. Regulatory compliance checks
"""

from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from .model_validator import ModelValidator

logger = logging.getLogger(__name__)

class HealthcareModelValidator(ModelValidator):
    """Healthcare-specific model validator."""
    
    def __init__(self, model_name: str, model_version: str):
        """Initialize the healthcare model validator.
        
        Args:
            model_name: Name of the model being validated
            model_version: Version of the model being validated
        """
        super().__init__(model_name, model_version)
        
        # Healthcare-specific validation rules
        self.healthcare_rules = {
            "age_distribution": {
                "type": "range",
                "name": "age_range_check",
                "description": "Check if age predictions/classifications are within valid ranges",
                "range": (0, 120)
            },
            "bmi_distribution": {
                "type": "range",
                "name": "bmi_range_check",
                "description": "Check if BMI predictions are within valid ranges",
                "range": (10, 60)
            },
            "cost_distribution": {
                "type": "distribution",
                "name": "cost_distribution_check",
                "description": "Check if cost predictions follow expected distribution",
                "expected_mean": 13000,  # Example value, should be configured based on actual data
                "expected_std": 5000
            }
        }
        
        # Protected healthcare attributes for fairness checking
        self.protected_attributes = [
            "age",
            "sex",
            "race",
            "ethnicity",
            "disability_status"
        ]
        
        # Regulatory compliance thresholds
        self.compliance_thresholds = {
            "minimum_accuracy": 0.90,
            "maximum_bias": 0.10,
            "maximum_disparity": 0.15
        }
    
    def validate_healthcare_outputs(self, outputs: np.ndarray,
                                 output_type: str,
                                 metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate healthcare-specific model outputs.
        
        Args:
            outputs: Model output values to validate
            output_type: Type of healthcare output (e.g., 'age', 'bmi', 'cost')
            metadata: Additional metadata about the outputs
            
        Returns:
            Dictionary containing healthcare-specific validation results
            
        Raises:
            ValueError: If output_type is invalid or outputs array is empty
        """
        # Validate inputs
        if len(outputs) == 0:
            raise ValueError("Empty outputs array provided")
            
        if output_type not in self.healthcare_rules:
            raise ValueError(f"Invalid output_type: {output_type}. Must be one of: {list(self.healthcare_rules.keys())}")
            
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "output_type": output_type,
            "healthcare_specific_checks": []
        }
        
        try:
            # Apply healthcare-specific rules based on output type
            if output_type in self.healthcare_rules:
                rule = self.healthcare_rules[output_type]
                check_result = self._apply_validation_rule(outputs, rule)
                validation_results["healthcare_specific_checks"].append(check_result)
            
            # Additional healthcare-specific validations
            validation_results.update({
                "clinical_validity": self._check_clinical_validity(outputs, output_type, metadata),
                "regulatory_compliance": self._check_regulatory_compliance(outputs, metadata)
            })
            
            # Store in overall validation results
            self.validation_results["healthcare_validation"] = validation_results
            logger.info(f"Healthcare validation completed for {output_type}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in healthcare validation: {e}")
            raise
    
    def analyze_healthcare_bias(self, predictions: np.ndarray,
                              sensitive_features: pd.DataFrame,
                              target: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Analyze healthcare-specific biases and disparities.
        
        Args:
            predictions: Model predictions
            sensitive_features: DataFrame containing sensitive healthcare attributes
            target: Optional ground truth values
            
        Returns:
            Dictionary containing healthcare-specific bias analysis
        """
        bias_results = {
            "timestamp": datetime.now().isoformat(),
            "protected_attributes": {},
            "healthcare_disparities": {},
            "compliance_status": "compliant"
        }
        
        try:
            # Analyze each protected healthcare attribute
            for attribute in self.protected_attributes:
                if attribute in sensitive_features.columns:
                    # Calculate healthcare-specific disparity metrics
                    attribute_results = self._analyze_healthcare_disparity(
                        predictions, 
                        sensitive_features[attribute],
                        target
                    )
                    
                    bias_results["protected_attributes"][attribute] = attribute_results
                    
                    # Check if any disparity exceeds compliance thresholds
                    if attribute_results.get("disparity_ratio", 1.0) > (1 + self.compliance_thresholds["maximum_disparity"]):
                        bias_results["compliance_status"] = "non_compliant"
            
            # Store in overall validation results
            self.validation_results["healthcare_bias"] = bias_results
            logger.info("Healthcare bias analysis completed")
            
            return bias_results
            
        except Exception as e:
            logger.error(f"Error in healthcare bias analysis: {e}")
            raise
    
    def _check_clinical_validity(self, outputs: np.ndarray, 
                               output_type: str,
                               metadata: Optional[Dict]) -> Dict[str, Any]:
        """Check clinical validity of model outputs.
        
        Args:
            outputs: Model outputs to validate
            output_type: Type of healthcare output
            metadata: Additional metadata about the outputs
            
        Returns:
            Dictionary containing clinical validity results
        """
        validity_results = {
            "clinically_valid": True,
            "warnings": []
        }
        
        try:
            if output_type == "cost":
                # Check for unrealistic cost predictions
                if np.any(outputs < 0):
                    validity_results["warnings"].append("Negative cost predictions detected")
                    validity_results["clinically_valid"] = False
                
                if np.any(outputs > 1000000):  # Example threshold
                    validity_results["warnings"].append("Extremely high cost predictions detected")
                    validity_results["clinically_valid"] = False
            
            elif output_type == "bmi":
                # Check for physiologically impossible BMI values
                if np.any(outputs < 10) or np.any(outputs > 60):
                    validity_results["warnings"].append("Physiologically impossible BMI values detected")
                    validity_results["clinically_valid"] = False
            
            # Add metadata-based checks if available
            if metadata and "clinical_context" in metadata:
                validity_results["context_specific"] = self._check_context_specific_validity(
                    outputs, 
                    output_type,
                    metadata["clinical_context"]
                )
            
            return validity_results
            
        except Exception as e:
            logger.error(f"Error in clinical validity check: {e}")
            validity_results["error"] = str(e)
            return validity_results
    
    def _check_regulatory_compliance(self, outputs: np.ndarray,
                                   metadata: Optional[Dict]) -> Dict[str, Any]:
        """Check regulatory compliance of model outputs.
        
        Args:
            outputs: Model outputs to validate
            metadata: Additional metadata about the outputs
            
        Returns:
            Dictionary containing compliance check results
        """
        compliance_results = {
            "compliant": True,
            "checks": []
        }
        
        try:
            # Check accuracy against minimum threshold
            if "accuracy" in self.validation_results.get("metrics", {}):
                accuracy = self.validation_results["metrics"]["accuracy"]
                compliance_results["checks"].append({
                    "name": "minimum_accuracy",
                    "passed": accuracy >= self.compliance_thresholds["minimum_accuracy"],
                    "value": accuracy,
                    "threshold": self.compliance_thresholds["minimum_accuracy"]
                })
            
            # Check bias against maximum threshold
            if "bias_analysis" in self.validation_results:
                bias_metrics = self.validation_results["bias_analysis"]
                max_disparity = 0
                for attribute in bias_metrics.get("group_disparities", {}):
                    disparities = bias_metrics["group_disparities"][attribute].get("disparities", {})
                    for metric, value in disparities.items():
                        if "ratio" in metric and value > max_disparity:
                            max_disparity = value
                
                compliance_results["checks"].append({
                    "name": "maximum_bias",
                    "passed": max_disparity <= (1 + self.compliance_thresholds["maximum_bias"]),
                    "value": max_disparity,
                    "threshold": 1 + self.compliance_thresholds["maximum_bias"]
                })
            
            # Update overall compliance status
            compliance_results["compliant"] = all(check["passed"] for check in compliance_results["checks"])
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"Error in regulatory compliance check: {e}")
            compliance_results["error"] = str(e)
            return compliance_results
    
    def _analyze_healthcare_disparity(self, predictions: np.ndarray,
                                    attribute_values: pd.Series,
                                    target: Optional[np.ndarray]) -> Dict[str, Any]:
        """Analyze healthcare-specific disparities for a protected attribute.
        
        Args:
            predictions: Model predictions
            attribute_values: Values of the protected attribute
            target: Optional ground truth values
            
        Returns:
            Dictionary containing healthcare disparity metrics
        """
        disparity_results = {
            "groups": {},
            "disparity_metrics": {}
        }
        
        try:
            unique_groups = attribute_values.unique()
            
            # Calculate healthcare-specific metrics for each group
            for group in unique_groups:
                group_mask = attribute_values == group
                group_preds = predictions[group_mask]
                
                group_metrics = {
                    "size": int(np.sum(group_mask)),
                    "mean_prediction": float(np.mean(group_preds)),
                    "std_prediction": float(np.std(group_preds))
                }
                
                # Add outcome metrics if target is available
                if target is not None:
                    group_target = target[group_mask]
                    group_metrics.update({
                        "outcome_rate": float(np.mean(group_target)),
                        "prediction_rate": float(np.mean(group_preds)),
                        "false_positive_rate": float(
                            np.sum((group_preds == 1) & (group_target == 0)) / 
                            np.sum(group_target == 0) if np.sum(group_target == 0) > 0 else 0
                        )
                    })
                
                disparity_results["groups"][str(group)] = group_metrics
            
            # Calculate disparity metrics
            if len(unique_groups) > 1:
                metrics = ["mean_prediction", "prediction_rate", "false_positive_rate"]
                for metric in metrics:
                    values = [g.get(metric, 0) for g in disparity_results["groups"].values()]
                    if values and not all(v == 0 for v in values):
                        min_val = min(v for v in values if v > 0)
                        max_val = max(values)
                        disparity_results["disparity_metrics"][metric] = {
                            "ratio": float(max_val / min_val) if min_val > 0 else float('inf'),
                            "difference": float(max_val - min_val)
                        }
            
            return disparity_results
            
        except Exception as e:
            logger.error(f"Error in healthcare disparity analysis: {e}")
            return {"error": str(e)}
    
    def _check_context_specific_validity(self, outputs: np.ndarray,
                                       output_type: str,
                                       clinical_context: Dict) -> Dict[str, Any]:
        """Check validity in specific clinical contexts.
        
        Args:
            outputs: Model outputs to validate
            output_type: Type of healthcare output
            clinical_context: Dictionary containing clinical context
            
        Returns:
            Dictionary containing context-specific validity results
        """
        context_results = {
            "valid": True,
            "context_specific_warnings": []
        }
        
        try:
            # Example context-specific checks
            if clinical_context.get("setting") == "emergency":
                # Stricter thresholds for emergency settings
                if output_type == "cost":
                    high_cost_threshold = clinical_context.get("high_cost_threshold", 50000)
                    high_cost_predictions = np.sum(outputs > high_cost_threshold)
                    if high_cost_predictions > 0:
                        context_results["context_specific_warnings"].append(
                            f"{high_cost_predictions} predictions exceed emergency cost threshold"
                        )
            
            elif clinical_context.get("population") == "pediatric":
                # Special checks for pediatric populations
                if output_type == "bmi":
                    # Use pediatric-specific BMI ranges
                    if np.any(outputs > 40):
                        context_results["context_specific_warnings"].append(
                            "Extremely high BMI predictions for pediatric population"
                        )
            
            context_results["valid"] = len(context_results["context_specific_warnings"]) == 0
            return context_results
            
        except Exception as e:
            logger.error(f"Error in context-specific validity check: {e}")
            context_results["error"] = str(e)
            return context_results