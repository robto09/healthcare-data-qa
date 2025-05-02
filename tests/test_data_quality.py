"""
Healthcare Data QA Automation - Data Quality Tests

This module provides tests for:
1. Data completeness checks
2. Data consistency checks
3. Statistical validation
4. Healthcare-specific validation rules

Author: Robert Torres
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data_quality.base_check import BaseCheck
from src.data_quality.null_check import NullCheck
from src.data_quality.schema_check import SchemaCheck
from src.data_quality.anomaly_check import AnomalyCheck

class TestDataQualityChecks:
    """Test suite for data quality validation checks."""
    
    def test_null_check(self, test_data):
        """Test null value detection and reporting."""
        # Create data with nulls
        df = test_data.copy()
        df.loc[0, 'age'] = None
        df.loc[1, 'bmi'] = None
        
        # Run null check
        checker = NullCheck()
        results = checker.run(df)
        
        assert results is not None
        assert 'null_counts' in results
        assert results['null_counts']['age'] == 1
        assert results['null_counts']['bmi'] == 1
        assert results['total_null_percentage'] > 0
    
    def test_schema_validation(self, test_data):
        """Test data schema validation."""
        expected_columns = ['age', 'sex', 'bmi', 'children', 'smoker', 'region', 'charges']
        column_types = {
            'age': np.int64,
            'bmi': np.float64,
            'children': np.int64,
            'charges': np.float64
        }
        checker = SchemaCheck(expected_columns=expected_columns, column_types=column_types)
        results = checker.run(test_data)
        
        assert results is not None
        assert results['schema_valid'] is True
        assert len(results['type_violations']) == 0
        
        # Test with invalid data
        df = test_data.copy()
        df['age'] = df['age'].astype(str)  # Convert age to string
        results = checker.run(df)
        
        assert results['schema_valid'] is False
        assert len(results['type_violations']) > 0
        assert 'age' in results['type_violations']
    
    def test_anomaly_detection(self, test_data):
        """Test statistical anomaly detection."""
        checker = AnomalyCheck()
        results = checker.run(test_data)
        
        assert results is not None
        assert 'anomalies' in results
        assert isinstance(results['anomalies'], dict)
        # Check specific anomaly results
        assert 'stats_summary' in results
        assert 'z_threshold' in results
        assert 'columns_checked' in results
        
        # Test with artificial outlier
        df = test_data.copy()
        df.loc[0, 'charges'] = 1000000  # Add extreme value
        results = checker.run(df)
        
        assert results['anomalies']['charges']['count'] > 0
        assert 0 in results['anomalies']['charges']['indices']  # Index 0 should be flagged
    
    def test_value_range_validation(self, test_data):
        """Test value range validation for healthcare data."""
        class RangeCheck(BaseCheck):
            def run(self, df):
                issues = []
                
                # Age validation
                invalid_age = df[~df['age'].between(0, 120)].index
                if len(invalid_age) > 0:
                    issues.append({
                        'column': 'age',
                        'issue': 'invalid_range',
                        'indices': invalid_age.tolist()
                    })
                
                # BMI validation
                invalid_bmi = df[~df['bmi'].between(10, 70)].index
                if len(invalid_bmi) > 0:
                    issues.append({
                        'column': 'bmi',
                        'issue': 'invalid_range',
                        'indices': invalid_bmi.tolist()
                    })
                
                return {'range_issues': issues}
        
        checker = RangeCheck()
        results = checker.run(test_data)
        
        assert results is not None
        assert 'range_issues' in results
        assert len(results['range_issues']) == 0
        
        # Test with invalid values
        df = test_data.copy()
        df.loc[0, 'age'] = 150
        df.loc[1, 'bmi'] = 5
        results = checker.run(df)
        
        assert len(results['range_issues']) == 2
    
    def test_categorical_validation(self, test_data):
        """Test categorical value validation."""
        class CategoricalCheck(BaseCheck):
            def run(self, df):
                issues = []
                
                # Sex validation
                invalid_sex = df[~df['sex'].isin(['male', 'female'])].index
                if len(invalid_sex) > 0:
                    issues.append({
                        'column': 'sex',
                        'issue': 'invalid_category',
                        'indices': invalid_sex.tolist()
                    })
                
                # Region validation
                valid_regions = ['southwest', 'southeast', 'northwest', 'northeast']
                invalid_region = df[~df['region'].isin(valid_regions)].index
                if len(invalid_region) > 0:
                    issues.append({
                        'column': 'region',
                        'issue': 'invalid_category',
                        'indices': invalid_region.tolist()
                    })
                
                return {'category_issues': issues}
        
        checker = CategoricalCheck()
        results = checker.run(test_data)
        
        assert results is not None
        assert 'category_issues' in results
        assert len(results['category_issues']) == 0
        
        # Test with invalid categories
        df = test_data.copy()
        df.loc[0, 'sex'] = 'other'
        df.loc[1, 'region'] = 'central'
        results = checker.run(df)
        
        assert len(results['category_issues']) == 2
    
    def test_correlation_analysis(self, test_data):
        """Test correlation analysis between features."""
        def check_correlations(df):
            # Select only numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            corr_matrix = numeric_df.corr()
            strong_correlations = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    correlation = corr_matrix.iloc[i, j]
                    if abs(correlation) > 0.7:  # Strong correlation threshold
                        strong_correlations.append({
                            'feature1': corr_matrix.columns[i],
                            'feature2': corr_matrix.columns[j],
                            'correlation': correlation
                        })
            
            return strong_correlations
        
        correlations = check_correlations(test_data)
        assert isinstance(correlations, list)
        
        # Test with artificial correlation
        df = test_data.copy()
        df['age_squared'] = df['age'] * df['age']  # Perfect correlation
        correlations = check_correlations(df)
        
        assert len(correlations) > 0
        assert any(c['feature1'] == 'age' and c['feature2'] == 'age_squared' 
                  for c in correlations)

    def test_completeness_check(self, test_data):
        """Test data completeness validation."""
        def check_completeness(df):
            total_rows = len(df)
            completeness = {}
            
            for column in df.columns:
                valid_count = df[column].notna().sum()
                completeness[column] = {
                    'valid_count': valid_count,
                    'missing_count': total_rows - valid_count,
                    'completeness_ratio': valid_count / total_rows
                }
            
            return completeness
        
        results = check_completeness(test_data)
        
        assert results is not None
        for column in test_data.columns:
            assert column in results
            assert results[column]['completeness_ratio'] == 1.0
        
        # Test with missing values
        df = test_data.copy()
        df.loc[0:2, 'age'] = None
        results = check_completeness(df)
        
        assert results['age']['missing_count'] == 3
        assert results['age']['completeness_ratio'] < 1.0