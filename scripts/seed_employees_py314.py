"""
Seed 10,000 realistic employees into the database
Python 3.14 compatible (uses sqlite3 directly)
"""
import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = '../backend/salary_management.db'

FIRST_NAMES = [
    'James', 'Mary', 'Robert', 'Patricia', 'Michael', 'Jennifer', 'William', 'Linda', 'David', 'Barbara',
    'Richard', 'Elizabeth', 'Joseph', 'Susan', 'Thomas', 'Jessica', 'Charles', 'Sarah', 'Christopher', 'Karen',
    'Daniel', 'Nancy', 'Matthew', 'Lisa', 'Anthony', 'Betty', 'Donald', 'Margaret', 'Steven', 'Sandra',
    'Paul', 'Ashley', 'Andrew', 'Kathy', 'Joshua', 'Shirley', 'Kenneth', 'Angela', 'Kevin', 'Brenda',
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
    'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
    'Walker', 'Young', 'Alvarado', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Peterson', 'Phillips',
]

COUNTRIES = [
    'United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'India', 'China', 'Japan',
    'Australia', 'Brazil', 'Mexico', 'Netherlands', 'Singapore', 'Sweden', 'Switzerland',
]

JOB_TITLES = [
    'Software Engineer', 'Senior Software Engineer', 'Software Architect', 'Product Manager', 'Designer',
    'Data Scientist', 'Data Engineer', 'Project Manager', 'QA Engineer', 'DevOps Engineer',
    'Business Analyst', 'Sales Manager', 'Account Executive', 'Marketing Manager', 'HR Manager',
    'Finance Manager', 'Operations Manager', 'Support Engineer', 'Technical Writer', 'Solutions Architect',
]

DEPARTMENTS = [
    'Engineering', 'Product', 'Sales', 'Marketing', 'Human Resources', 'Finance', 'Operations',
    'Customer Support', 'Data Science', 'Quality Assurance',
]

# Salary multipliers by country
COUNTRY_SALARY_MULTIPLIER = {
    'United States': 1.0,
    'Canada': 0.95,
    'United Kingdom': 0.85,
    'Germany': 0.88,
    'France': 0.80,
    'India': 0.25,
    'China': 0.50,
    'Japan': 0.90,
    'Australia': 0.98,
    'Brazil': 0.40,
    'Mexico': 0.35,
    'Netherlands': 0.92,
    'Singapore': 0.95,
    'Sweden': 0.93,
    'Switzerland': 1.15,
}

# Base salaries by job title (USD equivalent)
BASE_SALARY = {
    'Software Engineer': 100000,
    'Senior Software Engineer': 150000,
    'Software Architect': 180000,
    'Product Manager': 140000,
    'Designer': 90000,
    'Data Scientist': 130000,
    'Data Engineer': 120000,
    'Project Manager': 110000,
    'QA Engineer': 85000,
    'DevOps Engineer': 125000,
    'Business Analyst': 95000,
    'Sales Manager': 120000,
    'Account Executive': 100000,
    'Marketing Manager': 110000,
    'HR Manager': 100000,
    'Finance Manager': 115000,
    'Operations Manager': 105000,
    'Support Engineer': 70000,
    'Technical Writer': 80000,
    'Solutions Architect': 160000,
}

def generate_salary(job_title, country):
    """Generate realistic salary based on job title and country"""
    base = BASE_SALARY.get(job_title, 100000)
    multiplier = COUNTRY_SALARY_MULTIPLIER.get(country, 1.0)
    # Add some randomness (±20%)
    variance = random.uniform(0.8, 1.2)
    return int(base * multiplier * variance)

def generate_email(first_name, last_name, index):
    """Generate unique email address"""
    base = f"{first_name.lower()}.{last_name.lower()}"
    # Add index to ensure uniqueness for 10,000+ employees
    return f"{base}{index}@company.com"

def generate_phone():
    """Generate random phone number"""
    return f"+{random.randint(1, 999)} {random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"

def seed_employees(count=10000, batch_size=1000):
    """Seed employees into the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print(f"Starting to seed {count} employees...")
    start_time = datetime.now()
    
    employees_to_insert = []
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        job_title = random.choice(JOB_TITLES)
        country = random.choice(COUNTRIES)
        department = random.choice(DEPARTMENTS)
        
        # Random hire date (up to 10 years ago)
        days_ago = random.randint(0, 3650)
        hire_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        employee = (
            f"{first_name} {last_name}",  # full_name
            first_name,
            last_name,
            job_title,
            country,
            generate_salary(job_title, country),
            department,
            generate_email(first_name, last_name, i),
            generate_phone(),
            hire_date,
            random.choice([True, True, True, False]),  # 75% active
        )
        
        employees_to_insert.append(employee)
        
        # Batch insert every batch_size records
        if (i + 1) % batch_size == 0:
            cursor.executemany('''
                INSERT INTO employees 
                (full_name, first_name, last_name, job_title, country, salary, department, email, phone, hire_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', employees_to_insert)
            conn.commit()
            employees_to_insert = []
            print(f"Inserted {i + 1}/{count} employees...")
    
    # Insert remaining employees
    if employees_to_insert:
        cursor.executemany('''
            INSERT INTO employees 
            (full_name, first_name, last_name, job_title, country, salary, department, email, phone, hire_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', employees_to_insert)
        conn.commit()
    
    conn.close()
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    print(f"\n✅ Successfully seeded {count} employees in {elapsed:.2f} seconds!")
    print(f"   Average: {elapsed/count*1000:.2f}ms per employee")

if __name__ == '__main__':
    try:
        seed_employees(10000)
    except Exception as e:
        print(f"❌ Error seeding employees: {e}")
        import traceback
        traceback.print_exc()
