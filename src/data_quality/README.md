# Data Quality Modules

This directory contains modules for performing data quality checks and validation on healthcare datasets.

## Modules

### Base Check (`base_check.py`)
- Base class for implementing data quality checks
- Defines common interface and utilities
- Provides abstract methods for validation

### Null Check (`null_check.py`)
- Detects missing values in datasets
- Calculates null percentages by column
- Reports null value distribution
- Validates against defined thresholds

### Schema Check (`schema_check.py`)
- Validates data structure and types
- Ensures column presence and data types
- Verifies field constraints
- Reports schema violations

### Anomaly Check (`anomaly_check.py`)
- Detects statistical outliers
- Uses Z-score based detection
- Identifies numerical anomalies
- Reports anomaly statistics

## Usage

```python
from src.data_quality.null_check import NullCheck
from src.data_quality.schema_check import SchemaCheck
from src.data_quality.anomaly_check import AnomalyCheck

# Initialize checker
checker = NullCheck()

# Run check on dataframe
results = checker.run(df)

# Process results
print(results['null_counts'])
print(results['total_null_percentage'])
```

## Configuration

Quality check thresholds and parameters can be configured in `config.json`:
- Null percentage threshold: 5%
- Anomaly Z-score threshold: 3
- Schema validation rules
- Custom validation parameters

## Output

Each check produces a standardized result dictionary containing:
- Check status (pass/fail)
- Detailed findings
- Statistics and metrics
- Recommendations for issues