"""
AI Model Validation Framework for healthcare data models.

This module provides comprehensive validation capabilities for AI/ML models:
1. Performance metrics tracking
2. Output validation
3. Bias detection
4. A/B testing
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import json
import logging
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_validation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelValidator:
    """Base class for AI model validation."""
    
    def __init__(self, model_name: str, model_version: str):
        """Initialize the model validator.
        
        Args:
            model_name: Name of the model being validated
            model_version: Version of the model being validated
        """
        self.model_name = model_name
        self.model_version = model_version
        self.validation_results = {
            "model_name": model_name,
            "model_version": model_version,
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "validation_checks": [],
            "bias_analysis": {},
            "performance_comparison": {}
        }
    
    def validate_performance(self, y_true: np.ndarray, y_pred: np.ndarray, 
                           y_prob: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Validate model performance using standard metrics.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            y_prob: Prediction probabilities (optional)
            
        Returns:
            Dictionary containing performance metrics
        """
        metrics = {}
        
        try:
            # Basic classification metrics
            metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
            metrics["precision"] = float(precision_score(y_true, y_pred, average='weighted'))
            metrics["recall"] = float(recall_score(y_true, y_pred, average='weighted'))
            metrics["f1"] = float(f1_score(y_true, y_pred, average='weighted'))
            
            # Add ROC AUC if probabilities are provided
            if y_prob is not None:
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob, multi_class='ovr'))
            
            # Add confusion matrix
            metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()
            
            # Store metrics in validation results
            self.validation_results["metrics"] = metrics
            logger.info(f"Performance validation completed for {self.model_name} v{self.model_version}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in performance validation: {e}")
            raise
    
    def validate_outputs(self, outputs: np.ndarray, 
                        expected_range: Optional[tuple] = None,
                        validation_rules: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Validate model outputs against defined rules and expectations.
        
        Args:
            outputs: Model output values to validate
            expected_range: Optional tuple of (min, max) expected values
            validation_rules: List of custom validation rules
            
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_outputs": len(outputs),
            "checks": []
        }
        
        try:
            # Basic statistical checks
            validation_results["statistics"] = {
                "mean": float(np.mean(outputs)),
                "std": float(np.std(outputs)),
                "min": float(np.min(outputs)),
                "max": float(np.max(outputs)),
                "median": float(np.median(outputs))
            }
            
            # Range validation if provided
            if expected_range:
                min_val, max_val = expected_range
                within_range = np.logical_and(outputs >= min_val, outputs <= max_val)
                validation_results["range_check"] = {
                    "within_range_percentage": float(np.mean(within_range) * 100),
                    "outliers_count": int(np.sum(~within_range))
                }
            
            # Custom validation rules
            if validation_rules:
                for rule in validation_rules:
                    check_result = self._apply_validation_rule(outputs, rule)
                    validation_results["checks"].append(check_result)
            
            # Store in overall validation results
            self.validation_results["validation_checks"].append(validation_results)
            logger.info(f"Output validation completed for {self.model_name}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in output validation: {e}")
            raise
    
    def analyze_bias(self, predictions: np.ndarray, sensitive_features: pd.DataFrame,
                    target: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Analyze model predictions for potential biases across sensitive features.
        
        Args:
            predictions: Model predictions
            sensitive_features: DataFrame containing sensitive attribute data
            target: Optional ground truth values for fairness metrics
            
        Returns:
            Dictionary containing bias analysis results
        """
        bias_results = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "group_disparities": {}
        }
        
        try:
            # Analyze each sensitive feature
            for column in sensitive_features.columns:
                group_metrics = {}
                unique_groups = sensitive_features[column].unique()
                
                # Calculate prediction statistics per group
                for group in unique_groups:
                    group_mask = sensitive_features[column] == group
                    group_preds = predictions[group_mask]
                    
                    group_metrics[str(group)] = {
                        "size": int(np.sum(group_mask)),
                        "mean_prediction": float(np.mean(group_preds)),
                        "std_prediction": float(np.std(group_preds))
                    }
                    
                    # Add fairness metrics if target is provided
                    if target is not None:
                        group_target = target[group_mask]
                        group_metrics[str(group)].update({
                            "accuracy": float(accuracy_score(group_target, group_preds)),
                            "precision": float(precision_score(group_target, group_preds, average='weighted')),
                            "recall": float(recall_score(group_target, group_preds, average='weighted'))
                        })
                
                # Calculate disparities between groups
                disparities = self._calculate_group_disparities(group_metrics)
                
                bias_results["group_disparities"][column] = {
                    "group_metrics": group_metrics,
                    "disparities": disparities
                }
            
            # Store in overall validation results
            self.validation_results["bias_analysis"] = bias_results
            logger.info(f"Bias analysis completed for {self.model_name}")
            
            return bias_results
            
        except Exception as e:
            logger.error(f"Error in bias analysis: {e}")
            raise
    
    def compare_versions(self, other_version_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare validation results between model versions.
        
        Args:
            other_version_results: Validation results from another model version
            
        Returns:
            Dictionary containing version comparison results
        """
        comparison_results = {
            "timestamp": datetime.now().isoformat(),
            "base_version": self.model_version,
            "compare_version": other_version_results.get("model_version"),
            "metric_deltas": {},
            "significant_changes": []
        }
        
        try:
            # Compare performance metrics
            base_metrics = self.validation_results.get("metrics", {})
            other_metrics = other_version_results.get("metrics", {})
            
            for metric in base_metrics:
                if metric in other_metrics:
                    delta = base_metrics[metric] - other_metrics[metric]
                    delta_percentage = (delta / other_metrics[metric]) * 100 if other_metrics[metric] != 0 else float('inf')
                    
                    comparison_results["metric_deltas"][metric] = {
                        "absolute_change": float(delta),
                        "percentage_change": float(delta_percentage)
                    }
                    
                    # Flag significant changes (>5% change)
                    if abs(delta_percentage) > 5:
                        comparison_results["significant_changes"].append({
                            "metric": metric,
                            "change": float(delta_percentage),
                            "severity": "high" if abs(delta_percentage) > 10 else "medium"
                        })
            
            # Store in overall validation results
            self.validation_results["performance_comparison"] = comparison_results
            logger.info(f"Version comparison completed for {self.model_name}")
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error in version comparison: {e}")
            raise
    
    def _apply_validation_rule(self, outputs: np.ndarray, rule: Dict) -> Dict[str, Any]:
        """Apply a custom validation rule to model outputs.
        
        Args:
            outputs: Model outputs to validate
            rule: Dictionary containing rule definition
            
        Returns:
            Dictionary containing rule check results
        """
        check_result = {
            "rule_name": rule.get("name", "unnamed_rule"),
            "description": rule.get("description", ""),
            "passed": False,
            "details": {}
        }
        
        try:
            rule_type = rule.get("type", "")
            
            if rule_type == "range":
                min_val, max_val = rule.get("range", (None, None))
                if min_val is not None and max_val is not None:
                    within_range = np.logical_and(outputs >= min_val, outputs <= max_val)
                    check_result.update({
                        "passed": np.all(within_range),
                        "details": {
                            "within_range_percentage": float(np.mean(within_range) * 100),
                            "outliers_count": int(np.sum(~within_range))
                        }
                    })
            
            elif rule_type == "distribution":
                # Check if output distribution matches expected parameters
                expected_mean = rule.get("expected_mean")
                expected_std = rule.get("expected_std")
                if expected_mean is not None and expected_std is not None:
                    actual_mean = np.mean(outputs)
                    actual_std = np.std(outputs)
                    mean_diff = abs(actual_mean - expected_mean)
                    std_diff = abs(actual_std - expected_std)
                    
                    check_result.update({
                        "passed": mean_diff <= expected_std * 0.1 and std_diff <= expected_std * 0.1,
                        "details": {
                            "expected_mean": float(expected_mean),
                            "actual_mean": float(actual_mean),
                            "expected_std": float(expected_std),
                            "actual_std": float(actual_std)
                        }
                    })
            
            return check_result
            
        except Exception as e:
            logger.error(f"Error applying validation rule: {e}")
            check_result["error"] = str(e)
            return check_result
    
    def _calculate_group_disparities(self, group_metrics: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate disparities between groups.
        
        Args:
            group_metrics: Dictionary containing metrics for each group
            
        Returns:
            Dictionary containing disparity metrics
        """
        disparities = {}
        
        try:
            # Get list of metrics that exist for all groups
            first_group = next(iter(group_metrics.values()))
            metric_names = [k for k in first_group.keys() if isinstance(first_group[k], (int, float))]
            
            # Calculate max disparity for each metric
            for metric in metric_names:
                values = [g[metric] for g in group_metrics.values() if metric in g]
                if values:
                    min_val = min(values)
                    max_val = max(values)
                    # Calculate disparity ratio (max/min) and difference (max-min)
                    disparities[f"{metric}_ratio"] = float(max_val / min_val) if min_val != 0 else float('inf')
                    disparities[f"{metric}_difference"] = float(max_val - min_val)
            
            return disparities
            
        except Exception as e:
            logger.error(f"Error calculating group disparities: {e}")
            return {"error": str(e)}
    
    def save_results(self, output_dir: str = "validation_results") -> str:
        """Save validation results to a JSON file.
        
        Args:
            output_dir: Directory to save results
            
        Returns:
            Path to the saved file
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/{self.model_name}_{self.model_version}_{timestamp}.json"
            
            # Convert numpy types and other non-serializable objects to Python native types
            def convert_to_serializable(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, (np.bool_, bool)):
                    return bool(obj)
                elif isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(i) for i in obj]
                return obj
            
            # Convert results to serializable format
            serializable_results = convert_to_serializable(self.validation_results)
            
            # Save results
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            logger.info(f"Validation results saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving validation results: {e}")
            raise