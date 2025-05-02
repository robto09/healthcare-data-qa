# Healthcare Data QA Testing Documentation

This document outlines all test cases implemented in the Healthcare Data QA platform.

## 1. Web UI Tests (`tests/test_web_ui.py`)

### Prerequisites
Before running UI tests:
1. Start the Flask server:
```bash
python3 src/web/app.py
```
2. Ensure the server is running on http://localhost:5001
3. Wait for server initialization (usually takes a few seconds)

### Dashboard Tests
- **test_dashboard_loads**: Verifies that the main dashboard loads correctly with proper title and navigation
- **test_navigation**: Tests navigation between different pages (Dashboard, Tables, Quality Checks, API Docs)
- **test_data_visualization**: Validates chart rendering and data distribution visualization

### Quality Check UI Tests
- **test_quality_checks**: Tests the quality checks page functionality
  - Verifies "Run Quality Check" button presence
  - Validates results table structure
  - Checks status indicators and timestamps

### Tables View Tests
- **test_tables_page**: Tests database tables overview functionality
  - Validates table statistics display
  - Checks record counts and column information
  - Tests table detail view navigation

### Responsive Design Tests
- **test_responsive_layout**: Tests UI responsiveness across different screen sizes
  - Desktop (1920x1080)
  - Laptop (1366x768)
  - Tablet (768x1024)
  - Mobile (375x812)

### Error Handling Tests
- **test_error_handling**: Validates error page display and navigation recovery

## 2. Data Quality Tests (`tests/test_data_quality.py`)

### Null Value Tests
- **test_null_check**: Tests null value detection in datasets
  - Identifies missing values in specific columns (age, bmi, charges)
  - Calculates null percentages (threshold: 5%)
  - Reports null value distribution by column
  - Validates null handling in categorical fields
  - Success criteria: All critical fields < 5% null values

### Schema Validation Tests
- **test_schema_validation**: Validates data structure and types
  - Column presence verification (7 required fields)
  - Data type checking:
    * age: integer
    * sex: string (categorical)
    * bmi: float
    * children: integer
    * smoker: string (categorical)
    * region: string (categorical)
    * charges: float
  - Schema consistency validation across all records
  - Success criteria: 100% schema compliance

### Anomaly Detection Tests
- **test_anomaly_detection**: Tests statistical outlier detection
  - Z-score based anomaly detection (threshold: ±3σ)
  - Identifies numerical outliers in:
    * age: outside 0-120 range
    * bmi: outside 10-70 range
    * charges: extreme values (>3σ from mean)
  - Reports anomaly statistics with confidence intervals
  - Success criteria: <1% critical anomalies

### Value Range Tests
- **test_value_range_validation**: Validates value ranges for healthcare data
  - Age range validation:
    * Valid: 0-120 years
    * Warning: <18 or >90 years
  - BMI range validation:
    * Valid: 10-70
    * Warning: <15 or >45
  - Children count validation:
    * Valid: 0-10
    * Warning: >5
  - Insurance charges validation:
    * Valid: >0
    * Warning: >$50,000
  - Success criteria: 99% within valid ranges

### Categorical Data Tests
- **test_categorical_validation**: Tests categorical value validation
  - Sex categories:
    * Valid values: ["male", "female"]
    * Case-insensitive matching
  - Region validation:
    * Valid values: ["southwest", "southeast", "northwest", "northeast"]
    * Case-insensitive matching
  - Smoker status validation:
    * Valid values: ["yes", "no"]
    * Case-insensitive matching
  - Success criteria: 100% valid categories

### Statistical Tests
- **test_correlation_analysis**: Tests feature correlation analysis
  - Identifies correlations:
    * Strong: |r| > 0.7
    * Moderate: 0.4 < |r| < 0.7
    * Weak: |r| < 0.4
  - Analyzes relationships between:
    * age vs charges
    * bmi vs charges
    * smoker vs charges
  - Reports correlation matrices with p-values
  - Success criteria: Key correlations identified with p < 0.05

### Completeness Tests
- **test_completeness_check**: Validates data completeness
  - Column-wise completeness ratios:
    * Critical fields (age, sex, charges): 99.9% required
    * Other fields: 95% required
  - Missing value patterns analysis
  - Data quality metrics:
    * Completeness score
    * Consistency score
    * Validity score
  - Success criteria: Overall quality score >95%

## 3. ML Component Tests (`tests/unit/test_ml.py`)

### Text Processing Tests
- **test_01_preprocess_text**: Tests text preprocessing functionality
  - Special character removal:
    * Punctuation and symbol removal (accuracy: 100%)
    * Whitespace normalization
    * Special medical character handling
  - Number handling:
    * Numeric standardization (e.g., "1" vs "one")
    * Medical measurements conversion
    * Range format standardization
  - Case normalization:
    * Consistent lowercase conversion
    * Medical abbreviation preservation
    * Acronym handling
  - Stopword removal:
    * Domain-specific medical stopwords
    * Common English stopwords
    * Context-aware filtering
  - Success criteria: 100% standardized format

### Model Training Tests
- **test_02_train_model**: Validates model training process
  - Model initialization:
    * Architecture verification
    * Weight initialization checks
    * GPU/CPU resource allocation
  - Training execution:
    * Loss convergence (within 100 epochs)
    * Learning rate scheduling
    * Early stopping criteria
  - Metrics calculation:
    * RMSE < $5000 for cost prediction
    * R² > 0.85 for model fit
    * Cross-validation stability
  - Success criteria: All metrics within targets

### Prediction Tests
- **test_03_predict**: Tests prediction functionality
  - Single prediction validation:
    * Input format verification
    * Output range validation
    * Response time < 100ms
  - Multiple prediction handling:
    * Batch processing (up to 1000 records)
    * Memory efficiency
    * Concurrent request handling
  - Label consistency:
    * Value type validation
    * Range verification
    * Error handling
  - Success criteria: 95% accuracy

### Probability Tests
- **test_04_predict_proba**: Tests probability prediction
  - Probability distribution:
    * Range validation [0,1]
    * Distribution uniformity
    * Outlier detection
  - Confidence scores:
    * Threshold validation (>0.8 high confidence)
    * Uncertainty quantification
    * Calibration curves
  - Multi-class probability handling:
    * Class balance checks
    * Probability sum = 1.0
    * Class overlap analysis
  - Success criteria: Calibration error < 0.1

### Keyword Analysis Tests
- **test_05_extract_keywords**: Tests keyword extraction
  - Top-N keyword extraction:
    * N={5,10,20} keywords
    * Medical term prioritization
    * Relevance thresholds
  - Keyword scoring:
    * TF-IDF scoring
    * Domain relevance weighting
    * Context importance
  - Relevance ranking:
    * Expert validation
    * Semantic similarity
    * Usage frequency
  - Success criteria: >80% medical relevance

## 4. Model Validation Tests (`tests/unit/test_model_validation.py`)

### Healthcare Cost Predictor Tests
- **Performance Metrics Validation**:
  - Root Mean Square Error (RMSE):
    * Target: < $5,000 on test set
    * Cross-validation stability: σ < $500
    * Per-fold validation: all folds < $5,500
  - Mean Absolute Error (MAE):
    * Target: < $3,000 on test set
    * 90th percentile error < $4,000
    * Systematic bias check < $100
  - R-squared (R²):
    * Target: > 0.85 on test set
    * All cross-validation folds > 0.80
    * Adjusted R² within 0.02 of R²

- **Prediction Accuracy by Segment**:
  - Age-based accuracy:
    * Young (18-30): RMSE < $4,000
    * Adult (31-60): RMSE < $5,000
    * Senior (61+): RMSE < $6,000
  - Risk category accuracy:
    * Low risk: 90% predictions within ±$2,000
    * Medium risk: 85% within ±$4,000
    * High risk: 80% within ±$6,000
  - Regional performance:
    * Max RMSE variation < 20% across regions
    * Consistent bias checks across regions

- **Feature Importance Analysis**:
  - SHAP value validation:
    * Key feature identification
    * Importance ranking stability
    * Cross-validation consistency > 90%
  - Feature contribution thresholds:
    * Primary features: >15% impact
    * Secondary features: 5-15% impact
    * Tertiary features: <5% impact
  - Interaction effects:
    * Pairwise interaction strength
    * Multi-feature dependencies
    * Stability across data splits

- **Model Interpretability Validation**:
  - Local interpretability:
    * LIME explanation consistency
    * Case-specific feature impacts
    * Counterfactual analysis validity
  - Global interpretability:
    * Feature interaction patterns
    * Partial dependence plots
    * Accumulated local effects
  - Documentation quality:
    * Feature documentation completeness
    * Decision path clarity
    * Usage guideline coverage

- **Success Criteria**:
  - Overall RMSE < $5,000 on test set
  - R² > 0.85 across all validation sets
  - Feature importance stability > 90%
  - Interpretability score > 0.8
  - Documentation coverage > 95%

## Running Tests

### Prerequisites
- Python 3.8+
- pytest
- Selenium WebDriver (for UI tests)
- Required Python packages in requirements.txt

### Test Environment Setup
1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Set up test database:
```bash
python3 scripts/init_db.py
```

3. For UI tests, start the server:
```bash
# Terminal 1: Start Flask server
python3 src/web/app.py

# Terminal 2: Run UI tests (after server is running)
pytest tests/test_web_ui.py
```

### Execution Commands
```bash
# Run all tests (non-UI)
pytest tests/test_data_quality.py tests/unit/

# Run UI tests (requires running server)
python3 src/web/app.py  # Terminal 1
pytest tests/test_web_ui.py  # Terminal 2

# Run with coverage report
pytest --cov=src tests/
```

### CI/CD Integration
Tests are automatically run on:
- Pull request creation
- Main branch commits
- Release tagging

Note: CI/CD pipeline automatically handles server startup for UI tests.

## Test Coverage Goals
- Web UI: 90% coverage
- Data Quality: 95% coverage
- ML Components: 90% coverage
- Overall: 92% coverage

## Adding New Tests
1. Identify the appropriate test category
2. Create test file if needed
3. Implement test cases following existing patterns
4. Include docstrings and comments
5. Update this documentation