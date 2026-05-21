"""
Unit tests for Salary Management Tool Backend
"""
import pytest
from app import create_app
from models import db, Employee
from datetime import datetime

@pytest.fixture
def app():
    """Create app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_employee():
    """Create sample employee data"""
    return {
        'full_name': 'John Doe',
        'first_name': 'John',
        'last_name': 'Doe',
        'job_title': 'Software Engineer',
        'country': 'USA',
        'salary': 120000,
        'department': 'Engineering',
        'email': 'john.doe@company.com',
        'phone': '+1-555-0123',
    }

# ==================== CRUD TESTS ====================

def test_create_employee(client, sample_employee):
    """Test creating an employee"""
    response = client.post('/api/employees', json=sample_employee)
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['full_name'] == sample_employee['full_name']
    assert data['salary'] == sample_employee['salary']

def test_create_employee_missing_fields(client):
    """Test creating employee with missing required fields"""
    incomplete_data = {
        'full_name': 'John Doe',
        'email': 'john@company.com',
    }
    response = client.post('/api/employees', json=incomplete_data)
    assert response.status_code == 400

def test_create_employee_duplicate_email(client, sample_employee):
    """Test creating employee with duplicate email"""
    client.post('/api/employees', json=sample_employee)
    
    duplicate = sample_employee.copy()
    duplicate['full_name'] = 'Jane Doe'
    response = client.post('/api/employees', json=duplicate)
    assert response.status_code == 400

def test_get_employees(client, sample_employee):
    """Test getting employees list"""
    # Create multiple employees
    for i in range(3):
        emp = sample_employee.copy()
        emp['full_name'] = f"Employee {i}"
        emp['email'] = f"emp{i}@company.com"
        client.post('/api/employees', json=emp)
    
    response = client.get('/api/employees')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['total'] == 3
    assert len(data['data']) == 3

def test_get_employees_with_pagination(client, sample_employee):
    """Test getting employees with pagination"""
    # Create 10 employees
    for i in range(10):
        emp = sample_employee.copy()
        emp['full_name'] = f"Employee {i}"
        emp['email'] = f"emp{i}@company.com"
        client.post('/api/employees', json=emp)
    
    response = client.get('/api/employees?page=1&per_page=5')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data['data']) == 5
    assert data['total'] == 10
    assert data['pages'] == 2

def test_get_employees_filter_by_country(client, sample_employee):
    """Test filtering employees by country"""
    # Create employees in different countries
    emp1 = sample_employee.copy()
    emp1['email'] = 'emp1@company.com'
    emp1['country'] = 'USA'
    
    emp2 = sample_employee.copy()
    emp2['full_name'] = 'Jane Doe'
    emp2['email'] = 'emp2@company.com'
    emp2['country'] = 'UK'
    
    client.post('/api/employees', json=emp1)
    client.post('/api/employees', json=emp2)
    
    response = client.get('/api/employees?country=USA')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['total'] == 1
    assert data['data'][0]['country'] == 'USA'

def test_get_single_employee(client, sample_employee):
    """Test getting a single employee"""
    create_response = client.post('/api/employees', json=sample_employee)
    employee_id = create_response.get_json()['id']
    
    response = client.get(f'/api/employees/{employee_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['id'] == employee_id
    assert data['full_name'] == sample_employee['full_name']

def test_get_nonexistent_employee(client):
    """Test getting a non-existent employee"""
    response = client.get('/api/employees/99999')
    assert response.status_code == 404

def test_update_employee(client, sample_employee):
    """Test updating an employee"""
    create_response = client.post('/api/employees', json=sample_employee)
    employee_id = create_response.get_json()['id']
    
    update_data = {
        'salary': 150000,
        'job_title': 'Senior Software Engineer',
    }
    
    response = client.put(f'/api/employees/{employee_id}', json=update_data)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['salary'] == 150000
    assert data['job_title'] == 'Senior Software Engineer'

def test_update_nonexistent_employee(client):
    """Test updating a non-existent employee"""
    response = client.put('/api/employees/99999', json={'salary': 100000})
    assert response.status_code == 404

def test_delete_employee(client, sample_employee):
    """Test deleting an employee"""
    create_response = client.post('/api/employees', json=sample_employee)
    employee_id = create_response.get_json()['id']
    
    response = client.delete(f'/api/employees/{employee_id}')
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f'/api/employees/{employee_id}')
    assert response.status_code == 404

def test_delete_nonexistent_employee(client):
    """Test deleting a non-existent employee"""
    response = client.delete('/api/employees/99999')
    assert response.status_code == 404

# ==================== INSIGHTS TESTS ====================

def test_country_insights(client, sample_employee):
    """Test country salary insights"""
    # Create employees in same country
    for i in range(3):
        emp = sample_employee.copy()
        emp['full_name'] = f"Employee {i}"
        emp['email'] = f"emp{i}@company.com"
        emp['salary'] = 100000 + (i * 10000)
        client.post('/api/employees', json=emp)
    
    response = client.get('/api/insights/country/USA')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['country'] == 'USA'
    assert data['total_employees'] == 3
    assert data['min_salary'] == 100000
    assert data['max_salary'] == 120000
    assert data['average_salary'] == 110000.0

def test_job_title_insights(client, sample_employee):
    """Test job title salary insights"""
    emp1 = sample_employee.copy()
    emp1['email'] = 'emp1@company.com'
    emp1['job_title'] = 'Engineer'
    emp1['salary'] = 100000
    
    emp2 = sample_employee.copy()
    emp2['full_name'] = 'Jane Doe'
    emp2['email'] = 'emp2@company.com'
    emp2['job_title'] = 'Manager'
    emp2['salary'] = 110000
    
    client.post('/api/employees', json=emp1)
    client.post('/api/employees', json=emp2)
    
    response = client.get('/api/insights/job-title?job_title=Engineer&country=USA')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['total_employees'] == 1
    assert data['average_salary'] == 100000.0

def test_summary(client, sample_employee):
    """Test overall summary"""
    for i in range(5):
        emp = sample_employee.copy()
        emp['full_name'] = f"Employee {i}"
        emp['email'] = f"emp{i}@company.com"
        emp['salary'] = 100000 + (i * 5000)
        client.post('/api/employees', json=emp)
    
    response = client.get('/api/insights/summary')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['total_employees'] == 5

def test_get_all_countries(client, sample_employee):
    """Test getting all countries"""
    emp1 = sample_employee.copy()
    emp1['email'] = 'emp1@company.com'
    emp1['country'] = 'USA'
    
    emp2 = sample_employee.copy()
    emp2['full_name'] = 'Jane Doe'
    emp2['email'] = 'emp2@company.com'
    emp2['country'] = 'UK'
    
    client.post('/api/employees', json=emp1)
    client.post('/api/employees', json=emp2)
    
    response = client.get('/api/insights/countries')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 2

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'
