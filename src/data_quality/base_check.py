"""
Base class for data quality checks.

Author: Robert Torres
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseCheck(ABC):
    """Base class for implementing data quality checks."""

    def __init__(self):
        """Initialize the check."""
        self.results = {}

    @abstractmethod
    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run the data quality check.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary containing validation results
        """
        pass

    def get_results(self) -> Dict[str, Any]:
        """Get the results of the last check run."""
        return self.results
