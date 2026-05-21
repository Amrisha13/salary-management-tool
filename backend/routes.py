"""
API routes for Salary Management Tool
"""
from flask import Blueprint, request, jsonify
from models import db, Employee
from sqlalchemy import func
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprints
employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')
insights_bp = Blueprint('insights', __name__, url_prefix='/api/insights')

# ==================== EMPLOYEE CRUD ENDPOINTS ====================

@employees_bp.route('', methods=['POST'])
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['full_name', 'first_name', 'last_name', 'job_title', 'country', 'salary', 'email']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check duplicate email
        if Employee.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        employee = Employee(
            full_name=data['full_name'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            job_title=data['job_title'],
            country=data['country'],
            salary=int(data['salary']),
            department=data.get('department'),
            email=data['email'],
            phone=data.get('phone'),
            is_active=data.get('is_active', True),
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify(employee.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating employee: {str(e)}")
        return jsonify({'error': str(e)}), 500

@employees_bp.route('', methods=['GET'])
def get_employees():
    """Get all employees with pagination and filtering"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        country = request.args.get('country', type=str)
        job_title = request.args.get('job_title', type=str)
        is_active = request.args.get('is_active', type=str)
        
        # Build query
        query = Employee.query
        
        if country:
            query = query.filter_by(country=country)
        if job_title:
            query = query.filter_by(job_title=job_title)
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [emp.to_dict() for emp in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Get a single employee by ID"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify(employee.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error fetching employee: {str(e)}")
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Update an employee"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        for field in ['full_name', 'first_name', 'last_name', 'job_title', 'country', 'department', 'phone', 'is_active']:
            if field in data:
                setattr(employee, field, data[field])
        
        if 'salary' in data:
            employee.salary = int(data['salary'])
        
        if 'email' in data:
            # Check if email is unique (excluding current employee)
            existing = Employee.query.filter_by(email=data['email']).first()
            if existing and existing.id != employee_id:
                return jsonify({'error': 'Email already exists'}), 400
            employee.email = data['email']
        
        db.session.commit()
        
        return jsonify(employee.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating employee: {str(e)}")
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'message': 'Employee deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting employee: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== SALARY INSIGHTS ENDPOINTS ====================

@insights_bp.route('/country/<country>', methods=['GET'])
def get_country_insights(country):
    """Get salary insights for a specific country"""
    try:
        employees = Employee.query.filter_by(country=country, is_active=True).all()
        
        if not employees:
            return jsonify({'error': f'No employees found in {country}'}), 404
        
        salaries = [emp.salary for emp in employees]
        
        insights = {
            'country': country,
            'total_employees': len(employees),
            'min_salary': min(salaries),
            'max_salary': max(salaries),
            'average_salary': round(sum(salaries) / len(salaries), 2),
            'median_salary': sorted(salaries)[len(salaries) // 2] if salaries else 0,
            'salary_std_dev': round((sum((x - sum(salaries)/len(salaries))**2 for x in salaries) / len(salaries))**0.5, 2) if len(salaries) > 1 else 0,
        }
        
        return jsonify(insights), 200
    
    except Exception as e:
        logger.error(f"Error fetching country insights: {str(e)}")
        return jsonify({'error': str(e)}), 500

@insights_bp.route('/job-title', methods=['GET'])
def get_job_title_insights():
    """Get salary insights for a specific job title and country"""
    try:
        job_title = request.args.get('job_title')
        country = request.args.get('country')
        
        if not job_title or not country:
            return jsonify({'error': 'job_title and country parameters required'}), 400
        
        employees = Employee.query.filter_by(
            job_title=job_title,
            country=country,
            is_active=True
        ).all()
        
        if not employees:
            return jsonify({'error': 'No employees found with those criteria'}), 404
        
        salaries = [emp.salary for emp in employees]
        
        insights = {
            'job_title': job_title,
            'country': country,
            'total_employees': len(employees),
            'min_salary': min(salaries),
            'max_salary': max(salaries),
            'average_salary': round(sum(salaries) / len(salaries), 2),
        }
        
        return jsonify(insights), 200
    
    except Exception as e:
        logger.error(f"Error fetching job title insights: {str(e)}")
        return jsonify({'error': str(e)}), 500

@insights_bp.route('/summary', methods=['GET'])
def get_summary():
    """Get overall salary summary statistics"""
    try:
        result = db.session.query(
            func.count(Employee.id).label('total_employees'),
            func.avg(Employee.salary).label('avg_salary'),
            func.min(Employee.salary).label('min_salary'),
            func.max(Employee.salary).label('max_salary'),
            func.count(func.distinct(Employee.country)).label('countries'),
            func.count(func.distinct(Employee.job_title)).label('job_titles'),
        ).filter(Employee.is_active == True).first()
        
        summary = {
            'total_employees': result.total_employees or 0,
            'average_salary': round(float(result.avg_salary) if result.avg_salary else 0, 2),
            'min_salary': result.min_salary or 0,
            'max_salary': result.max_salary or 0,
            'countries': result.countries or 0,
            'job_titles': result.job_titles or 0,
        }
        
        return jsonify(summary), 200
    
    except Exception as e:
        logger.error(f"Error fetching summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@insights_bp.route('/countries', methods=['GET'])
def get_all_countries():
    """Get list of all countries with employee counts"""
    try:
        result = db.session.query(
            Employee.country,
            func.count(Employee.id).label('count'),
            func.avg(Employee.salary).label('avg_salary'),
        ).filter(Employee.is_active == True).group_by(Employee.country).all()
        
        countries = [
            {
                'country': r.country,
                'employee_count': r.count,
                'average_salary': round(float(r.avg_salary), 2),
            }
            for r in result
        ]
        
        return jsonify(countries), 200
    
    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}")
        return jsonify({'error': str(e)}), 500

@insights_bp.route('/job-titles', methods=['GET'])
def get_all_job_titles():
    """Get list of all job titles with statistics"""
    try:
        country = request.args.get('country')
        
        query = db.session.query(
            Employee.job_title,
            func.count(Employee.id).label('count'),
            func.avg(Employee.salary).label('avg_salary'),
        ).filter(Employee.is_active == True)
        
        if country:
            query = query.filter(Employee.country == country)
        
        result = query.group_by(Employee.job_title).all()
        
        job_titles = [
            {
                'job_title': r.job_title,
                'employee_count': r.count,
                'average_salary': round(float(r.avg_salary), 2),
            }
            for r in result
        ]
        
        return jsonify(job_titles), 200
    
    except Exception as e:
        logger.error(f"Error fetching job titles: {str(e)}")
        return jsonify({'error': str(e)}), 500
