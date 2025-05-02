"""
Null value validation check.

Author: Robert Torres
"""

from typing import Dict, Any
import pandas as pd
from .base_check import BaseCheck


class NullCheck(BaseCheck):
    """Check for null values in DataFrame columns."""

    def __init__(self, threshold: float = 0.1):
        """
        Initialize the null check.

        Args:
            threshold: Maximum allowed percentage of null values (default: 0.1 or 10%)
        """
        super().__init__()
        self.threshold = threshold

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run null value checks on DataFrame.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary containing validation results
        """
        # Calculate null percentages
        null_counts = df.isnull().sum()
        null_percentages = null_counts / len(df)
        
        # Identify columns exceeding threshold
        failed_columns = null_percentages[null_percentages > self.threshold]
        
        # Calculate total null percentage
        total_nulls = null_counts.sum()
        total_cells = len(df) * len(df.columns)
        total_null_percentage = (total_nulls / total_cells) * 100

        # Store results
        self.results = {
            'null_counts': null_counts.to_dict(),
            'null_percentages': null_percentages.to_dict(),
            'failed_columns': failed_columns.to_dict(),
            'total_null_percentage': total_null_percentage,
            'passed': len(failed_columns) == 0,
            'threshold': self.threshold
        }
        
        return self.results
