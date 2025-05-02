# Machine Learning Components

This directory contains machine learning modules for healthcare data validation and analysis.

## Components

### Healthcare Validator (`healthcare_validator.py`)
- Validates healthcare data quality
- Checks for medical data consistency
- Validates ranges for health metrics
- Ensures coding standard compliance

### Model Validator (`model_validator.py`)
- Validates ML model performance
- Checks prediction accuracy
- Analyzes model bias
- Validates feature importance

### Text Analyzer (`text_analyzer.py`)
- Processes medical text data
- Extracts key medical terms
- Analyzes clinical notes
- Validates medical terminology

## Features

### Data Validation
- Age range validation (0-120 years)
- BMI range checks (10-70)
- Blood pressure validation
- Lab value range checks

### Model Performance Metrics
- RMSE < $5,000 for cost prediction
- R² > 0.85 for model fit
- MAE < $3,000 for predictions
- Cross-validation stability

### Bias Detection
- Age group fairness
- Gender bias analysis
- Regional variation checks
- Socioeconomic fairness

### Feature Analysis
- SHAP value calculation
- Feature importance ranking
- Interaction detection
- Correlation analysis

## Usage

```python
from src.ml.model_validator import ModelValidator
from src.ml.healthcare_validator import HealthcareValidator

# Initialize validators
model_validator = ModelValidator()
health_validator = HealthcareValidator()

# Validate model
validation_results = model_validator.validate(model, test_data)

# Validate healthcare data
health_results = health_validator.validate(patient_data)
```

## Configuration

Model validation parameters in `config.json`:
```json
{
  "validation": {
    "rmse_threshold": 5000,
    "r2_threshold": 0.85,
    "mae_threshold": 3000,
    "bias_threshold": 0.1
  }
}
```

## Output

Validation results include:
- Performance metrics
- Bias analysis
- Feature importance
- Recommendations
- Validation status