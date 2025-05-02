"""
Statistical anomaly detection check.

Author: Robert Torres
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats
from .base_check import BaseCheck


class AnomalyCheck(BaseCheck):
    """Check for statistical anomalies in numeric columns."""

    def __init__(self, z_threshold: float = 1.5, columns: List[str] = None):
        """
        Initialize the anomaly check.

        Args:
            z_threshold: Z-score threshold for anomaly detection (default: 3.0)
            columns: List of columns to check (if None, checks all numeric columns)
        """
        super().__init__()
        self.z_threshold = z_threshold
        self.columns = columns

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run anomaly detection on DataFrame.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary containing validation results
        """
        # Select columns to analyze
        if self.columns is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            columns_to_check = numeric_cols
        else:
            columns_to_check = [col for col in self.columns if col in df.columns]

        anomalies = {}
        stats_summary = {}
        
        for col in columns_to_check:
            # Calculate z-scores for the entire column
            series = df[col]
            mean = series.mean()
            std = series.std()
            
            # Handle zero standard deviation
            if std == 0:
                z_scores = np.zeros(len(series))
            else:
                z_scores = np.abs((series - mean) / std)
            
            # Identify anomalies using modified z-score method
            anomaly_mask = z_scores > self.z_threshold
            anomaly_indices = series.index[anomaly_mask].tolist()
            anomaly_values = series[anomaly_mask].tolist()
            
            # Calculate statistics
            stats_summary[col] = {
                'mean': df[col].mean(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'q1': df[col].quantile(0.25),
                'median': df[col].median(),
                'q3': df[col].quantile(0.75)
            }
            
            anomalies[col] = {
                'count': len(anomaly_indices),
                'indices': anomaly_indices,  # Already a list
                'values': anomaly_values,    # Already a list
                'percentage': (len(anomaly_indices) / len(df)) * 100
            }

        # Store results
        self.results = {
            'anomalies': anomalies,
            'stats_summary': stats_summary,
            'z_threshold': self.z_threshold,
            'columns_checked': list(columns_to_check),
            'passed': all(info['count'] == 0 for info in anomalies.values())
        }
        
        return self.results
