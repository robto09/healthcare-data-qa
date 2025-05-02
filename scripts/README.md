# Utility Scripts

This directory contains utility scripts for setting up and maintaining the Healthcare Data QA platform.

## Scripts

### Download Dataset (`download_dataset.py`)
Downloads the Medical Cost Personal dataset from GitHub:
```bash
python3 scripts/download_dataset.py
```
- Source: https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv
- Downloads to: data/insurance.csv
- Contains: age, sex, bmi, children, smoker, region, charges

### Initialize Database (`init_db.py`)
Sets up the SQLite database with required tables:
```bash
python3 scripts/init_db.py
```
- Creates database at location specified in DB_PATH (.env)
- Creates tables: patients, insurance_charges
- Loads data from insurance.csv
- Creates views for analytics

### Setup Script (`setup.py`)
Project setup utilities:
```bash
python3 scripts/setup.py
```
- Validates environment
- Creates required directories
- Sets up logging
- Initializes configurations

## Usage Order

1. Download dataset:
```bash
python3 scripts/download_dataset.py
```

2. Initialize database:
```bash
python3 scripts/init_db.py
```

3. Run setup utilities:
```bash
python3 scripts/setup.py
```

## Configuration

Scripts use configuration from:
- Environment variables (.env file)
- config.json
- Command line arguments

## Error Handling

All scripts include:
- Input validation
- Error logging
- Helpful error messages
- Cleanup on failure