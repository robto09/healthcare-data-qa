#!/usr/bin/env python3
"""
Setup script for Healthcare Data QA Automation Framework.
This script:
1. Creates necessary database structures
2. Downloads sample datasets
3. Sets up initial configuration
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create database directory if it doesn't exist
os.makedirs('data/db', exist_ok=True)

def create_database():
    """Create SQLite database with tables for healthcare data"""
    print("Creating database...")
    
    # Connect to SQLite database (will be created if it doesn't exist)
    conn = sqlite3.connect('data/db/healthcare.db')
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        date_of_birth DATE,
        gender TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        phone_number TEXT,
        email TEXT,
        insurance_provider TEXT,
        insurance_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create encounters table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS encounters (
        encounter_id TEXT PRIMARY KEY,
        patient_id TEXT,
        provider_id TEXT,
        encounter_date DATE,
        encounter_type TEXT,
        reason TEXT,
        diagnosis_codes TEXT,
        procedure_codes TEXT,
        medications TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
    )
    ''')
    
    # Create providers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS providers (
        provider_id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        specialty TEXT,
        npi_number TEXT,
        facility_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create facilities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS facilities (
        facility_id TEXT PRIMARY KEY,
        name TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        phone_number TEXT,
        type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create lab_results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lab_results (
        result_id TEXT PRIMARY KEY,
        patient_id TEXT,
        encounter_id TEXT,
        test_name TEXT,
        test_code TEXT,
        result_value TEXT,
        result_unit TEXT,
        reference_range TEXT,
        abnormal_flag TEXT,
        result_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
        FOREIGN KEY (encounter_id) REFERENCES encounters (encounter_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

def generate_sample_data():
    """Generate synthetic healthcare data for testing"""
    print("Generating sample data...")
    
    fake = Faker()
    Faker.seed(42)  # For reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Connect to the database
    conn = sqlite3.connect('data/db/healthcare.db')
    cursor = conn.cursor()
    
    # Generate facilities data
    facilities = []
    facility_types = ['Hospital', 'Clinic', 'Urgent Care', 'Laboratory', 'Imaging Center']
    
    for i in range(10):
        facility_id = f"FAC{i+1:04d}"
        facilities.append({
            'facility_id': facility_id,
            'name': fake.company() + ' ' + random.choice(['Hospital', 'Medical Center', 'Clinic', 'Care']),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip_code': fake.zipcode(),
            'phone_number': fake.phone_number(),
            'type': random.choice(facility_types)
        })
    
    # Insert facilities data
    for facility in facilities:
        cursor.execute('''
        INSERT INTO facilities (facility_id, name, address, city, state, zip_code, phone_number, type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            facility['facility_id'],
            facility['name'],
            facility['address'],
            facility['city'],
            facility['state'],
            facility['zip_code'],
            facility['phone_number'],
            facility['type']
        ))
    
    # Generate providers data
    providers = []
    specialties = ['Family Medicine', 'Internal Medicine', 'Cardiology', 'Neurology', 'Orthopedics', 
                  'Pediatrics', 'Obstetrics', 'Gynecology', 'Psychiatry', 'Dermatology']
    
    for i in range(50):
        provider_id = f"PRV{i+1:04d}"
        providers.append({
            'provider_id': provider_id,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'specialty': random.choice(specialties),
            'npi_number': f"{random.randint(1000000000, 9999999999)}",
            'facility_id': random.choice(facilities)['facility_id']
        })
    
    # Insert providers data
    for provider in providers:
        cursor.execute('''
        INSERT INTO providers (provider_id, first_name, last_name, specialty, npi_number, facility_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            provider['provider_id'],
            provider['first_name'],
            provider['last_name'],
            provider['specialty'],
            provider['npi_number'],
            provider['facility_id']
        ))
    
    # Generate patients data
    patients = []
    genders = ['Male', 'Female', 'Other', 'Unknown']
    insurance_providers = ['Medicare', 'Medicaid', 'Blue Cross', 'Aetna', 'UnitedHealth', 'Cigna', 'Humana']
    
    for i in range(200):
        patient_id = f"PAT{i+1:06d}"
        gender = random.choice(genders)
        first_name = fake.first_name_male() if gender == 'Male' else fake.first_name_female() if gender == 'Female' else fake.first_name()
        
        # Generate a date of birth between 1940 and 2010
        dob = fake.date_of_birth(minimum_age=10, maximum_age=80)
        
        patients.append({
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': fake.last_name(),
            'date_of_birth': dob.strftime('%Y-%m-%d'),
            'gender': gender,
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip_code': fake.zipcode(),
            'phone_number': fake.phone_number(),
            'email': fake.email(),
            'insurance_provider': random.choice(insurance_providers),
            'insurance_id': f"{random.randint(10000000, 99999999)}"
        })
    
    # Insert patients data
    for patient in patients:
        cursor.execute('''
        INSERT INTO patients (
            patient_id, first_name, last_name, date_of_birth, gender, 
            address, city, state, zip_code, phone_number, 
            email, insurance_provider, insurance_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient['patient_id'],
            patient['first_name'],
            patient['last_name'],
            patient['date_of_birth'],
            patient['gender'],
            patient['address'],
            patient['city'],
            patient['state'],
            patient['zip_code'],
            patient['phone_number'],
            patient['email'],
            patient['insurance_provider'],
            patient['insurance_id']
        ))
    
    # Generate encounters data
    encounters = []
    encounter_types = ['Office Visit', 'Emergency', 'Inpatient', 'Outpatient', 'Telehealth', 'Home Health']
    reasons = ['Annual Physical', 'Illness', 'Follow-up', 'Chronic Disease Management', 'Preventive Care', 'Injury']
    diagnosis_codes = ['E11.9', 'I10', 'J45.909', 'F41.1', 'M54.5', 'K21.9', 'G43.909', 'N39.0', 'L40.0', 'H60.339']
    procedure_codes = ['99213', '99214', '99215', '99396', '99397', '99203', '99204', '99205', '99285', '99284']
    medications = ['Lisinopril', 'Metformin', 'Atorvastatin', 'Levothyroxine', 'Albuterol', 'Omeprazole', 
                  'Amlodipine', 'Metoprolol', 'Gabapentin', 'Sertraline']
    
    # Current date for reference
    current_date = datetime.now()
    
    for i in range(1000):
        encounter_id = f"ENC{i+1:08d}"
        patient = random.choice(patients)
        provider = random.choice(providers)
        
        # Generate encounter date within the last 2 years
        days_back = random.randint(1, 730)
        encounter_date = (current_date - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Generate random number of diagnoses, procedures, and medications
        num_diagnoses = random.randint(1, 3)
        num_procedures = random.randint(1, 2)
        num_meds = random.randint(0, 3)
        
        encounters.append({
            'encounter_id': encounter_id,
            'patient_id': patient['patient_id'],
            'provider_id': provider['provider_id'],
            'encounter_date': encounter_date,
            'encounter_type': random.choice(encounter_types),
            'reason': random.choice(reasons),
            'diagnosis_codes': ','.join(random.sample(diagnosis_codes, num_diagnoses)),
            'procedure_codes': ','.join(random.sample(procedure_codes, num_procedures)),
            'medications': ','.join(random.sample(medications, num_meds)),
            'notes': fake.paragraph(nb_sentences=3)
        })
    
    # Insert encounters data
    for encounter in encounters:
        cursor.execute('''
        INSERT INTO encounters (
            encounter_id, patient_id, provider_id, encounter_date, 
            encounter_type, reason, diagnosis_codes, procedure_codes, 
            medications, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            encounter['encounter_id'],
            encounter['patient_id'],
            encounter['provider_id'],
            encounter['encounter_date'],
            encounter['encounter_type'],
            encounter['reason'],
            encounter['diagnosis_codes'],
            encounter['procedure_codes'],
            encounter['medications'],
            encounter['notes']
        ))
    
    # Generate lab results data
    lab_results = []
    test_names = ['Complete Blood Count', 'Basic Metabolic Panel', 'Comprehensive Metabolic Panel', 
                 'Lipid Panel', 'Hemoglobin A1C', 'Thyroid Stimulating Hormone', 'Urinalysis',
                 'Liver Function Tests', 'Vitamin D', 'Prostate Specific Antigen']
    test_codes = ['CBC', 'BMP', 'CMP', 'LIPID', 'A1C', 'TSH', 'UA', 'LFT', 'VITD', 'PSA']
    units = ['g/dL', 'mg/dL', 'U/L', 'mmol/L', '%', 'mIU/L', 'ng/mL', 'mcg/L']
    abnormal_flags = ['', '', '', 'H', 'L', '', '', '']  # More empty strings to make normal results more common
    
    for i in range(2000):
        result_id = f"LAB{i+1:08d}"
        
        # Select a random encounter
        encounter = random.choice(encounters)
        patient_id = encounter['patient_id']
        encounter_id = encounter['encounter_id']
        
        # Select a random test
        test_index = random.randint(0, len(test_names) - 1)
        test_name = test_names[test_index]
        test_code = test_codes[test_index]
        
        # Generate result date on or after encounter date
        encounter_date = datetime.strptime(encounter['encounter_date'], '%Y-%m-%d')
        days_after = random.randint(0, 5)  # Results typically come back within a few days
        result_date = (encounter_date + timedelta(days=days_after)).strftime('%Y-%m-%d')
        
        # Generate result value and other details
        result_value = str(round(random.uniform(1, 200), 1))
        result_unit = random.choice(units)
        reference_range = f"{round(random.uniform(1, 100), 1)}-{round(random.uniform(100, 200), 1)}"
        abnormal_flag = random.choice(abnormal_flags)
        
        lab_results.append({
            'result_id': result_id,
            'patient_id': patient_id,
            'encounter_id': encounter_id,
            'test_name': test_name,
            'test_code': test_code,
            'result_value': result_value,
            'result_unit': result_unit,
            'reference_range': reference_range,
            'abnormal_flag': abnormal_flag,
            'result_date': result_date
        })
    
    # Insert lab results data
    for result in lab_results:
        cursor.execute('''
        INSERT INTO lab_results (
            result_id, patient_id, encounter_id, test_name, test_code,
            result_value, result_unit, reference_range, abnormal_flag, result_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result['result_id'],
            result['patient_id'],
            result['encounter_id'],
            result['test_name'],
            result['test_code'],
            result['result_value'],
            result['result_unit'],
            result['reference_range'],
            result['abnormal_flag'],
            result['result_date']
        ))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Sample data generated successfully!")

def create_config_files():
    """Create configuration files for the project"""
    print("Creating configuration files...")
    
    # Create .env file
    with open('.env', 'w') as f:
        f.write('''# Environment Configuration
DB_PATH=data/db/healthcare.db
API_HOST=localhost
API_PORT=5000
DEBUG=True
''')
    
    print("Configuration files created successfully!")

def main():
    """Main setup function"""
    print("Setting up Healthcare Data QA Automation Framework...")
    
    create_database()
    generate_sample_data()
    create_config_files()
    
    print("\nSetup completed successfully!")
    print("You can now run the application with: python src/api/app.py")
    print("Or run data quality checks with: python src/data_quality/run_checks.py")

if __name__ == "__main__":
    main()
