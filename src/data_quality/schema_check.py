"""
Schema validation check.

Author: Robert Torres
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from .base_check import BaseCheck


class SchemaCheck(BaseCheck):
    """Check DataFrame schema against expected schema."""

    def __init__(self, expected_columns: List[str], required_columns: List[str] = None,
                 column_types: Dict[str, type] = None):
        """
        Initialize the schema check.

        Args:
            expected_columns: List of expected column names
            required_columns: List of required column names (must be present)
        """
        super().__init__()
        self.expected_columns = set(expected_columns)
        self.required_columns = set(required_columns or [])
        self.column_types = column_types or {}

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run schema validation on DataFrame.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary containing validation results
        """
        actual_columns = set(df.columns)
        
        # Check for missing required columns
        missing_required = self.required_columns - actual_columns
        
        # Check for missing expected columns
        missing_expected = self.expected_columns - actual_columns
        
        # Check for unexpected columns
        unexpected_columns = actual_columns - self.expected_columns
        
        # Check column types
        type_violations = {}
        for col, expected_type in self.column_types.items():
            if col in df.columns:
                actual_type = df[col].dtype
                # Handle numeric type comparisons
                if np.issubdtype(expected_type, np.number):
                    if not np.issubdtype(actual_type, expected_type):
                        type_violations[col] = {
                            'expected': str(expected_type),
                            'actual': str(actual_type)
                        }
                # Handle non-numeric type comparisons
                else:
                    if actual_type != expected_type:
                        type_violations[col] = {
                            'expected': str(expected_type),
                            'actual': str(actual_type)
                        }

        # Store results
        self.results = {
            'missing_required': list(missing_required),
            'missing_expected': list(missing_expected),
            'unexpected_columns': list(unexpected_columns),
            'type_violations': type_violations,
            'passed': len(missing_required) == 0,
            'actual_columns': list(actual_columns),
            'expected_columns': list(self.expected_columns),
            'required_columns': list(self.required_columns),
            'schema_valid': (len(missing_required) == 0 and
                           len(missing_expected) == 0 and
                           len(type_violations) == 0)
        }
        
        return self.results
