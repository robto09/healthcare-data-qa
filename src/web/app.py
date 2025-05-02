"""Flask web application for healthcare data quality dashboard."""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')

# Get database path from environment
DB_PATH = os.getenv('DB_PATH', 'data/db/healthcare.db')

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Render the dashboard homepage."""
    conn = get_db_connection()
    
    # Get table statistics
    cursor = conn.execute('''
        SELECT 'patients' as table_name, COUNT(*) as count FROM patients
        UNION ALL
        SELECT 'insurance_charges', COUNT(*) FROM insurance_charges
    ''')
    table_counts = {row['table_name']: row['count'] for row in cursor.fetchall()}
    
    # Get recent quality check results
    recent_results = []
    quality_results_dir = 'data/quality_results'
    if os.path.exists(quality_results_dir):
        for filename in sorted(os.listdir(quality_results_dir), reverse=True)[:5]:
            if filename.endswith('.json'):
                with open(os.path.join(quality_results_dir, filename)) as f:
                    result = json.load(f)
                    result['filename'] = filename
                    result['issue_count'] = len(result.get('issues', []))
                    recent_results.append(result)
    
    conn.close()
    return render_template('index.html', 
                         table_counts=table_counts,
                         recent_results=recent_results)

@app.route('/tables')
def tables():
    """Render the tables overview page."""
    conn = get_db_connection()
    
    # Get table information
    tables = []
    
    # Patients table info
    cursor = conn.execute('SELECT COUNT(*) as count FROM patients')
    patient_count = cursor.fetchone()['count']
    cursor = conn.execute('PRAGMA table_info(patients)')
    patient_columns = len(cursor.fetchall())
    tables.append({
        'name': 'patients',
        'count': patient_count,
        'columns': patient_columns
    })
    
    # Insurance charges table info
    cursor = conn.execute('SELECT COUNT(*) as count FROM insurance_charges')
    charges_count = cursor.fetchone()['count']
    cursor = conn.execute('PRAGMA table_info(insurance_charges)')
    charges_columns = len(cursor.fetchall())
    tables.append({
        'name': 'insurance_charges',
        'count': charges_count,
        'columns': charges_columns
    })
    
    conn.close()
    return render_template('tables.html', tables=tables)

@app.route('/table/<table_name>')
def table_detail(table_name):
    """Render detailed view of a specific table."""
    conn = get_db_connection()
    
    if table_name == 'patients':
        # Get patient statistics
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total_patients,
                AVG(age) as avg_age,
                AVG(bmi) as avg_bmi,
                SUM(children) as total_children,
                COUNT(CASE WHEN smoker = 'yes' THEN 1 END) as smoker_count
            FROM patients
        ''')
        stats = cursor.fetchone()
        
        # Get region distribution
        cursor = conn.execute('''
            SELECT region, COUNT(*) as count
            FROM patients
            GROUP BY region
        ''')
        regions = cursor.fetchall()
        
        return render_template('table_detail.html',
                             table_name=table_name,
                             stats=stats,
                             regions=regions)
    
    elif table_name == 'insurance_charges':
        # Get charges statistics
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total_charges,
                AVG(charges) as avg_charges,
                MIN(charges) as min_charges,
                MAX(charges) as max_charges
            FROM insurance_charges
        ''')
        stats = cursor.fetchone()
        
        return render_template('table_detail.html',
                             table_name=table_name,
                             stats=stats)
    
    conn.close()
    flash('Invalid table name', 'danger')
    return redirect(url_for('tables'))

@app.route('/quality')
def quality():
    """Render the quality checks page."""
    quality_results = []
    quality_results_dir = 'data/quality_results'
    
    if os.path.exists(quality_results_dir):
        for filename in sorted(os.listdir(quality_results_dir), reverse=True):
            if filename.endswith('.json'):
                with open(os.path.join(quality_results_dir, filename)) as f:
                    result = json.load(f)
                    result['filename'] = filename
                    result['issue_count'] = len(result.get('issues', []))
                    quality_results.append(result)
    
    return render_template('quality.html', quality_results=quality_results)

@app.route('/quality/run', methods=['POST'])
def run_quality_check():
    """Run quality checks on the database."""
    try:
        import os
        import sys
        # Add project root to Python path
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        
        from src.data_quality import run_all_checks
        results = run_all_checks(DB_PATH)
        flash(f"Successfully ran {len(results)} quality checks", "success")
    except Exception as e:
        app.logger.error(f"Error running quality checks: {str(e)}")
        flash("Error running quality checks", "danger")
    
    return redirect(url_for('quality'))

@app.route('/quality/result/<filename>')
def quality_result(filename):
    """Render a specific quality check result."""
    try:
        with open(os.path.join('data/quality_results', filename)) as f:
            result = json.load(f)
            return render_template('quality_result.html', result=result)
    except:
        flash('Quality check result not found', 'danger')
        return redirect(url_for('quality'))

@app.route('/api-docs')
def api_docs():
    """Render the API documentation page."""
    return render_template('api_docs.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    flash('Page not found', 'danger')
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    flash('Internal server error', 'danger')
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('src/web/templates', exist_ok=True)
    os.makedirs('src/web/static', exist_ok=True)
    
    # Get host and port from environment
    host = os.getenv('WEB_HOST', 'localhost')
    port = int(os.getenv('WEB_PORT', 5001))
    debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    
    app.run(host=host, port=port, debug=debug)
