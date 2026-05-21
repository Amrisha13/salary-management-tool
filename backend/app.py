"""
Salary Management Tool - Flask Backend (Python 3.14 Compatible)
Uses sqlite3 directly instead of SQLAlchemy for compatibility
"""
import sqlite3
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = 'salary_management.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            country TEXT NOT NULL,
            salary INTEGER NOT NULL,
            department TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            hire_date TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON employees(country)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_title ON employees(job_title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_salary ON employees(salary)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_active ON employees(is_active)')
    
    conn.commit()
    conn.close()

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# ==================== EMPLOYEE CRUD ====================

@app.route('/api/employees', methods=['POST'])
def create_employee():
    try:
        data = request.get_json()
        
        # Validation
        required = ['full_name', 'first_name', 'last_name', 'job_title', 'country', 'salary', 'email']
        if not all(f in data for f in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check duplicate email
        cursor.execute('SELECT id FROM employees WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            return jsonify({'error': 'Email already exists'}), 400
        
        cursor.execute('''
            INSERT INTO employees 
            (full_name, first_name, last_name, job_title, country, salary, department, email, phone, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['full_name'], data['first_name'], data['last_name'], 
            data['job_title'], data['country'], int(data['salary']),
            data.get('department'), data['email'], data.get('phone'),
            data.get('is_active', True)
        ))
        
        employee_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        employee = dict_from_row(cursor.fetchone())
        conn.close()
        
        return jsonify(employee), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        country = request.args.get('country', type=str)
        job_title = request.args.get('job_title', type=str)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Build query
        where_clauses = []
        params = []
        
        if country:
            where_clauses.append('country LIKE ?')
            params.append(f'%{country}%')
        if job_title:
            where_clauses.append('job_title LIKE ?')
            params.append(f'%{job_title}%')
        
        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        # Get total count
        cursor.execute(f'SELECT COUNT(*) as count FROM employees WHERE {where_sql}', params)
        total = cursor.fetchone()['count']
        
        # Get paginated results
        offset = (page - 1) * per_page
        cursor.execute(
            f'SELECT * FROM employees WHERE {where_sql} LIMIT ? OFFSET ?',
            params + [per_page, offset]
        )
        
        employees = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()
        
        pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'data': employees,
            'total': total,
            'pages': pages,
            'current_page': page,
            'per_page': per_page,
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        employee = cursor.fetchone()
        conn.close()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify(dict_from_row(employee)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Employee not found'}), 404
        
        updates = []
        params = []
        
        for field in ['full_name', 'first_name', 'last_name', 'job_title', 'country', 'department', 'phone', 'is_active']:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])
        
        if 'salary' in data:
            updates.append('salary = ?')
            params.append(int(data['salary']))
        
        if 'email' in data:
            cursor.execute('SELECT id FROM employees WHERE email = ? AND id != ?', (data['email'], employee_id))
            if cursor.fetchone():
                return jsonify({'error': 'Email already exists'}), 400
            updates.append('email = ?')
            params.append(data['email'])
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(employee_id)
            
            cursor.execute(f'UPDATE employees SET {", ".join(updates)} WHERE id = ?', params)
            conn.commit()
        
        cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        employee = dict_from_row(cursor.fetchone())
        conn.close()
        
        return jsonify(employee), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM employees WHERE id = ?', (employee_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Employee not found'}), 404
        
        cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Employee deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== INSIGHTS ====================

@app.route('/api/insights/summary', methods=['GET'])
def get_summary():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                ROUND(AVG(salary), 2) as avg_salary,
                MIN(salary) as min_salary,
                MAX(salary) as max_salary,
                COUNT(DISTINCT country) as countries,
                COUNT(DISTINCT job_title) as job_titles
            FROM employees WHERE is_active = 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        summary = {
            'total_employees': row['total'] or 0,
            'average_salary': row['avg_salary'] or 0,
            'min_salary': row['min_salary'] or 0,
            'max_salary': row['max_salary'] or 0,
            'countries': row['countries'] or 0,
            'job_titles': row['job_titles'] or 0,
        }
        
        return jsonify(summary), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/country/<country>', methods=['GET'])
def get_country_insights(country):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count, 
                   MIN(salary) as min_salary,
                   MAX(salary) as max_salary,
                   AVG(salary) as avg_salary
            FROM employees 
            WHERE country = ? AND is_active = 1
        ''', (country,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or row['count'] == 0:
            return jsonify({'error': f'No employees found in {country}'}), 404
        
        # Calculate median
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT salary FROM employees 
            WHERE country = ? AND is_active = 1
            ORDER BY salary
        ''', (country,))
        salaries = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        median = salaries[len(salaries)//2] if salaries else 0
        
        insights = {
            'country': country,
            'total_employees': row['count'],
            'min_salary': row['min_salary'],
            'max_salary': row['max_salary'],
            'average_salary': round(row['avg_salary'], 2),
            'median_salary': median,
        }
        
        return jsonify(insights), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/countries', methods=['GET'])
def get_all_countries():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT country, COUNT(*) as employee_count, ROUND(AVG(salary), 2) as average_salary
            FROM employees WHERE is_active = 1
            GROUP BY country
            ORDER BY employee_count DESC
        ''')
        
        countries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(countries), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/job-titles', methods=['GET'])
def get_all_job_titles():
    try:
        country = request.args.get('country')
        
        conn = get_db()
        cursor = conn.cursor()
        
        if country:
            cursor.execute('''
                SELECT job_title, COUNT(*) as employee_count, ROUND(AVG(salary), 2) as average_salary
                FROM employees 
                WHERE country = ? AND is_active = 1
                GROUP BY job_title
                ORDER BY employee_count DESC
            ''', (country,))
        else:
            cursor.execute('''
                SELECT job_title, COUNT(*) as employee_count, ROUND(AVG(salary), 2) as average_salary
                FROM employees WHERE is_active = 1
                GROUP BY job_title
                ORDER BY employee_count DESC
            ''')
        
        job_titles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(job_titles), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/job-title', methods=['GET'])
def get_job_title_insights():
    try:
        job_title = request.args.get('job_title')
        country = request.args.get('country')
        
        if not job_title or not country:
            return jsonify({'error': 'job_title and country parameters required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count,
                   MIN(salary) as min_salary,
                   MAX(salary) as max_salary,
                   AVG(salary) as avg_salary
            FROM employees 
            WHERE job_title = ? AND country = ? AND is_active = 1
        ''', (job_title, country))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or row['count'] == 0:
            return jsonify({'error': 'No employees found with those criteria'}), 404
        
        insights = {
            'job_title': job_title,
            'country': country,
            'total_employees': row['count'],
            'min_salary': row['min_salary'],
            'max_salary': row['max_salary'],
            'average_salary': round(row['avg_salary'], 2),
        }
        
        return jsonify(insights), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
