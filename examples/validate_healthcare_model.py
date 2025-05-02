"""
Script demonstrating the use of healthcare model validation framework
with the Medical Cost Personal dataset.

This script shows how to:
1. Load and preprocess the Medical Cost Personal dataset
2. Train a simple cost prediction model
3. Validate the model using our healthcare-specific framework
4. Generate and save validation reports
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import logging
from pathlib import Path

# Import our validators
from src.ml.healthcare_validator import HealthcareModelValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthcareCostModel:
    """Simple healthcare cost prediction model."""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        self.label_encoders = {}
        self.version = "1.0.0"
    
    def preprocess_data(self, df: pd.DataFrame) -> tuple:
        """Preprocess the healthcare dataset.
        
        Args:
            df: Raw DataFrame containing healthcare data
            
        Returns:
            Tuple of (X, y) with processed features and target
        """
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['sex', 'smoker', 'region']
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df_processed[col] = self.label_encoders[col].fit_transform(df_processed[col])
        
        # Split features and target
        X = df_processed.drop('charges', axis=1)
        y = df_processed['charges']
        
        return X, y
    
    def train(self, X: pd.DataFrame, y: pd.Series):
        """Train the model."""
        self.model.fit(X, y)
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate predictions."""
        return self.model.predict(X)

def load_dataset(data_path: str) -> pd.DataFrame:
    """Load the Medical Cost Personal dataset.
    
    Args:
        data_path: Path to the dataset CSV file
        
    Returns:
        DataFrame containing the dataset
    """
    try:
        df = pd.read_csv(data_path)
        logger.info(f"Loaded dataset with {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        raise

def main():
    """Main execution function."""
    try:
        # Load dataset
        data_path = "data/insurance.csv"
        df = load_dataset(data_path)
        
        # Create and train model
        model = HealthcareCostModel()
        X, y = model.preprocess_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        logger.info("Training model...")
        model.train(X_train, y_train)
        
        # Generate predictions
        y_pred = model.predict(X_test)
        
        # Initialize healthcare validator
        validator = HealthcareModelValidator(
            model_name="healthcare_cost_predictor",
            model_version=model.version
        )
        
        logger.info("Running healthcare-specific validation...")
        
        # Validate model outputs
        validator.validate_healthcare_outputs(
            outputs=y_pred,
            output_type='cost_distribution',
            metadata={
                'clinical_context': {
                    'setting': 'standard',
                    'high_cost_threshold': 50000
                }
            }
        )
        
        # Analyze potential biases
        sensitive_features = pd.DataFrame({
            'age': X_test['age'],
            'sex': X_test['sex'].map(
                dict(zip(range(len(model.label_encoders['sex'].classes_)),
                        model.label_encoders['sex'].classes_))
            ),
            'region': X_test['region'].map(
                dict(zip(range(len(model.label_encoders['region'].classes_)),
                        model.label_encoders['region'].classes_))
            )
        })
        
        validator.analyze_healthcare_bias(
            predictions=y_pred,
            sensitive_features=sensitive_features,
            target=y_test
        )
        
        # Calculate regression metrics
        validation_metrics = {
            'mse': np.mean((y_test - y_pred) ** 2),
            'rmse': np.sqrt(np.mean((y_test - y_pred) ** 2)),
            'mae': np.mean(np.abs(y_test - y_pred)),
            'r2': 1 - np.sum((y_test - y_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2)
        }
        
        # Add metrics to validation results
        validator.validation_results['metrics'].update(validation_metrics)
        
        # Check regulatory compliance
        validator._check_regulatory_compliance(
            y_pred,
            metadata={'clinical_context': {'setting': 'standard'}}
        )
        
        # Save validation results
        output_dir = "validation_results"
        os.makedirs(output_dir, exist_ok=True)
        results_path = validator.save_results(output_dir)
        
        logger.info(f"Validation results saved to: {results_path}")
        
        # Print summary metrics
        print("\nValidation Summary:")
        print(f"MSE: {validation_metrics['mse']:.2f}")
        print(f"RMSE: {validation_metrics['rmse']:.2f}")
        print(f"MAE: {validation_metrics['mae']:.2f}")
        print(f"R2 Score: {validation_metrics['r2']:.2f}")
        
        # Print bias analysis summary
        bias_results = validator.validation_results.get('healthcare_bias', {})
        print("\nBias Analysis Summary:")
        for attribute, results in bias_results.get('protected_attributes', {}).items():
            print(f"\n{attribute} disparities:")
            for metric, value in results.get('disparity_metrics', {}).items():
                print(f"  {metric}: {value['ratio']:.2f} (ratio), {value['difference']:.2f} (difference)")
        
        print(f"\nCompliance Status: {bias_results.get('compliance_status', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Error in validation process: {e}")
        raise

if __name__ == "__main__":
    main()