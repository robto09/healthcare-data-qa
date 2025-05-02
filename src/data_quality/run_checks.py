"""Run data quality checks on healthcare data."""

import sqlite3
import json
from datetime import datetime
import os
import pandas as pd
import numpy as np

def check_null_values(conn, table_name):
    """Check for null values in all columns of a table."""
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    null_counts = df.isnull().sum()
    
    issues = []
    for column in null_counts.index:
        if null_counts[column] > 0:
            issues.append({
                "type": "null_value",
                "column": column,
                "count": int(null_counts[column]),
                "details": f"Found {null_counts[column]} null values in column {column}"
            })
    
    return {
        "check_name": "Null Value Check",
        "table": table_name,
        "status": "failed" if issues else "passed",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "issues": issues
    }

def check_value_ranges(conn, table_name):
    """Check if numeric values are within expected ranges."""
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    range_checks = {
        "patients": {
            "age": (0, 120),
            "bmi": (10, 60),
            "children": (0, 10)
        },
        "insurance_charges": {
            "charges": (0, 100000)
        }
    }
    
    issues = []
    if table_name in range_checks:
        for column, (min_val, max_val) in range_checks[table_name].items():
            if column in df.columns:
                out_of_range = df[
                    (df[column] < min_val) | (df[column] > max_val)
                ]
                if not out_of_range.empty:
                    issues.append({
                        "type": "out_of_range",
                        "column": column,
                        "count": len(out_of_range),
                        "details": f"Found {len(out_of_range)} values outside range [{min_val}, {max_val}] in column {column}"
                    })
    
    return {
        "check_name": "Value Range Check",
        "table": table_name,
        "status": "failed" if issues else "passed",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "issues": issues
    }

def check_data_consistency(conn):
    """Check data consistency between related tables."""
    patient_ids_charges = pd.read_sql_query(
        "SELECT DISTINCT patient_id FROM insurance_charges", 
        conn
    )
    patient_ids_main = pd.read_sql_query(
        "SELECT id FROM patients", 
        conn
    )
    
    missing_patients = set(patient_ids_charges['patient_id']) - set(patient_ids_main['id'])
    orphaned_charges = set(patient_ids_main['id']) - set(patient_ids_charges['patient_id'])
    
    issues = []
    if missing_patients:
        issues.append({
            "type": "missing_reference",
            "details": f"Found {len(missing_patients)} insurance charges with non-existent patient IDs"
        })
    if orphaned_charges:
        issues.append({
            "type": "orphaned_record",
            "details": f"Found {len(orphaned_charges)} patients without insurance charges"
        })
    
    return {
        "check_name": "Data Consistency Check",
        "status": "failed" if issues else "passed",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "issues": issues
    }

def run_all_checks(db_path):
    """Run all quality checks and save results."""
    conn = sqlite3.connect(db_path)
    
    # Create results directory if it doesn't exist
    results_dir = "data/quality_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Run checks
    checks = []
    
    # Check patients table
    checks.append(check_null_values(conn, "patients"))
    checks.append(check_value_ranges(conn, "patients"))
    
    # Check insurance_charges table
    checks.append(check_null_values(conn, "insurance_charges"))
    checks.append(check_value_ranges(conn, "insurance_charges"))
    
    # Check relationships
    checks.append(check_data_consistency(conn))
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for i, result in enumerate(checks):
        filename = f"{timestamp}_{result['check_name'].replace(' ', '')}.json"
        with open(os.path.join(results_dir, filename), 'w') as f:
            json.dump(result, f, indent=2)
    
    conn.close()
    return checks

if __name__ == "__main__":
    db_path = os.getenv('DB_PATH', 'data/db/healthcare.db')
    run_all_checks(db_path)
