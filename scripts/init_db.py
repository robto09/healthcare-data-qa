#!/usr/bin/env python3
"""Initialize SQLite database with healthcare insurance data."""

import os
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Get database path from environment or use default
DB_PATH = os.getenv('DB_PATH', 'data/db/healthcare.db')

def init_db():
    """Initialize the database with healthcare insurance data."""
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Load the insurance dataset
    insurance_data = pd.read_csv('data/insurance.csv')
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables and views
    cursor.execute('DROP VIEW IF EXISTS region_statistics')
    cursor.execute('DROP VIEW IF EXISTS patient_charges')
    cursor.execute('DROP TABLE IF EXISTS insurance_charges')
    cursor.execute('DROP TABLE IF EXISTS patients')
    
    # Create patients table
    cursor.execute('''
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL,
        bmi REAL NOT NULL,
        children INTEGER NOT NULL,
        smoker TEXT NOT NULL,
        region TEXT NOT NULL
    )
    ''')
    
    # Create insurance_charges table
    cursor.execute('''
    CREATE TABLE insurance_charges (
        id INTEGER PRIMARY KEY,
        patient_id INTEGER NOT NULL,
        charges REAL NOT NULL,
        recorded_date TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )
    ''')
    
    # Insert data into patients table
    for _, row in insurance_data.iterrows():
        cursor.execute('''
        INSERT INTO patients (age, sex, bmi, children, smoker, region)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            int(row['age']),
            row['sex'],
            float(row['bmi']),
            int(row['children']),
            row['smoker'],
            row['region']
        ))
        
        # Get the patient_id for the insurance charges
        patient_id = cursor.lastrowid
        
        # Insert corresponding insurance charges
        cursor.execute('''
        INSERT INTO insurance_charges (patient_id, charges, recorded_date)
        VALUES (?, ?, ?)
        ''', (
            patient_id,
            float(row['charges']),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    # Create views for analytics
    cursor.execute('''
    CREATE VIEW patient_charges AS
    SELECT 
        p.id,
        p.age,
        p.sex,
        p.bmi,
        p.children,
        p.smoker,
        p.region,
        ic.charges
    FROM patients p
    JOIN insurance_charges ic ON p.id = ic.patient_id
    ''')
    
    # Create summary statistics view
    cursor.execute('''
    CREATE VIEW region_statistics AS
    SELECT 
        region,
        COUNT(*) as patient_count,
        AVG(charges) as avg_charges,
        MIN(charges) as min_charges,
        MAX(charges) as max_charges
    FROM patient_charges
    GROUP BY region
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {DB_PATH}")
    print(f"Loaded {len(insurance_data)} patient records")

if __name__ == '__main__':
    init_db()