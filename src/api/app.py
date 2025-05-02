#!/usr/bin/env python3
"""
API server for Healthcare Data QA Automation Framework.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_quality import NullValueCheck, SchemaValidationCheck, StatisticalAnomalyCheck

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Get database path from environment
DB_PATH = os.getenv('DB_PATH', 'data/db/healthcare.db')

def get_db_connection():
    """Get a connection to the SQLite database.
    
    Returns:
        tuple: (connection, cursor) to the database
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    return conn, cursor

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Get a list of all tables in the database.
    
    Returns:
        JSON: List of table names
    """
    try:
        conn, cursor = get_db_connection()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()
        return jsonify({'tables': tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>', methods=['GET'])
def get_table_schema(table_name):
    """Get the schema for a specific table.
    
    Args:
        table_name (str): Name of the table
        
    Returns:
        JSON: Table schema
    """
    try:
        conn, cursor = get_db_connection()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'table': table_name, 'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>/data', methods=['GET'])
def get_table_data(table_name):
    """Get data from a specific table.
    
    Args:
        table_name (str): Name of the table
        
    Returns:
        JSON: Table data
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        conn, cursor = get_db_connection()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
        data = [dict(row) for row in cursor.fetchall()]
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        total = cursor.fetchone()['count']
        
        conn.close()
        return jsonify({
            'table': table_name,
            'data': data,
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quality/null-check', methods=['POST'])
def run_null_check():
    """Run a null value check on specified table and columns.
    
    Request body:
        {
            "table": "table_name",
            "columns": ["column1", "column2", ...]
        }
        
    Returns:
        JSON: Check results
    """
    try:
        data = request.json
        table = data.get('table')
        columns = data.get('columns', [])
        
        if not table or not columns:
            return jsonify({'error': 'Table and columns are required'}), 400
        
        check = NullValueCheck(table, columns)
        results = check.run()
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quality/schema-check', methods=['POST'])
def run_schema_check():
    """Run a schema validation check.
    
    Request body:
        {
            "schema": {
                "table_name": {
                    "column_name": {
                        "type": "TEXT",
                        "nullable": true/false,
                        "primary_key": true/false
                    },
                    ...
                },
                ...
            }
        }
        
    Returns:
        JSON: Check results
    """
    try:
        data = request.json
        schema = data.get('schema', {})
        
        if not schema:
            return jsonify({'error': 'Schema is required'}), 400
        
        check = SchemaValidationCheck(schema)
        results = check.run()
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quality/anomaly-check', methods=['POST'])
def run_anomaly_check():
    """Run a statistical anomaly check.
    
    Request body:
        {
            "table": "table_name",
            "column": "column_name",
            "method": "zscore" or "iqr",
            "threshold": 3.0
        }
        
    Returns:
        JSON: Check results
    """
    try:
        data = request.json
        table = data.get('table')
        column = data.get('column')
        method = data.get('method', 'zscore')
        threshold = data.get('threshold', 3.0)
        
        if not table or not column:
            return jsonify({'error': 'Table and column are required'}), 400
        
        check = StatisticalAnomalyCheck(table, column, method, threshold)
        results = check.run()
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quality/results', methods=['GET'])
def get_quality_results():
    """Get a list of all quality check results.
    
    Returns:
        JSON: List of result files
    """
    try:
        results_dir = 'data/quality_results'
        if not os.path.exists(results_dir):
            return jsonify({'results': []})
        
        result_files = []
        for filename in os.listdir(results_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(results_dir, filename)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                result_files.append({
                    'filename': filename,
                    'check_name': data.get('check_name', 'Unknown'),
                    'status': data.get('status', 'unknown'),
                    'timestamp': data.get('timestamp', ''),
                    'issue_count': len(data.get('issues', []))
                })
        
        return jsonify({'results': result_files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quality/results/<filename>', methods=['GET'])
def get_quality_result(filename):
    """Get a specific quality check result.
    
    Args:
        filename (str): Name of the result file
        
    Returns:
        JSON: Check result
    """
    try:
        results_dir = 'data/quality_results'
        file_path = os.path.join(results_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Result file not found'}), 404
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('src/api/templates', exist_ok=True)
    os.makedirs('src/api/static', exist_ok=True)
    
    # Get host and port from environment
    host = os.getenv('API_HOST', 'localhost')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    
    app.run(host=host, port=port, debug=debug)
