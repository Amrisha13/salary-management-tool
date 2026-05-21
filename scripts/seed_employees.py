"""
Optimized seeding script for 10,000 employees
Performance-focused with batch inserts
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, Employee
import random
from datetime import datetime, timedelta
import time

# Sample data
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William", "Linda",
    "David", "Barbara", "Richard", "Elizabeth", "Joseph", "Susan", "Thomas", "Jessica",
    "Charles", "Sarah", "Christopher", "Karen", "Daniel", "Nancy", "Matthew", "Betty",
    "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley", "Paul", "Kimberly",
    "Andrew", "Donna", "Joshua", "Emily", "Kenneth", "Michelle", "Kevin", "Dorothy",
    "Brian", "Carol", "George", "Amanda", "Edward", "Melissa", "Ronald", "Deborah",
    "Anthony", "Stephanie", "Frank", "Rebecca", "Ryan", "Sharon", "Gary", "Laura",
    "Nicholas", "Cynthia", "Eric", "Kathleen", "Jonathan", "Amy", "Stephen", "Angela",
    "Larry", "Shirley", "Justin", "Anna", "Scott", "Brenda", "Brandon", "Pamela",
    "Benjamin", "Nicole", "Samuel", "Emma", "Raymond", "Helen", "Patrick", "Samantha",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Peterson", "Phillips", "Campbell",
    "Parker", "Evans", "Edwards", "Collins", "Reeves", "Stewart", "Morris", "Rogers",
    "Morgan", "Peterson", "Cooper", "Reed", "Cook", "Morgan", "Bell", "Murphy",
    "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Cox",
    "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Chavez", "Wood",
    "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes", "Price", "Alvarez",
]

COUNTRIES = [
    "USA", "UK", "Canada", "India", "Australia", "Germany", "France", "Japan",
    "Singapore", "China", "Brazil", "Mexico", "Netherlands", "Sweden", "Ireland",
]

JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Manager", "Product Manager",
    "Data Scientist", "Data Analyst", "DevOps Engineer", "QA Engineer",
    "HR Manager", "Finance Manager", "Sales Manager", "Marketing Manager",
    "Business Analyst", "System Administrator", "Network Engineer",
    "UI/UX Designer", "Full Stack Developer", "Backend Engineer", "Frontend Engineer",
    "Tech Lead", "Engineering Manager", "VP Engineering", "Chief Technology Officer",
]

DEPARTMENTS = [
    "Engineering", "Product", "Sales", "Marketing", "Finance", "HR",
    "Operations", "Legal", "Support", "Data", "Security", "Infrastructure",
]

def generate_salary(job_title, country):
    """Generate realistic salary based on job title and country"""
    base_salaries = {
        "Software Engineer": 100000,
        "Senior Software Engineer": 150000,
        "Manager": 120000,
        "Product Manager": 140000,
        "Data Scientist": 130000,
        "Data Analyst": 90000,
        "DevOps Engineer": 120000,
        "QA Engineer": 85000,
        "Business Analyst": 95000,
        "VP Engineering": 250000,
        "Chief Technology Officer": 300000,
    }
    
    country_multipliers = {
        "USA": 1.0,
        "UK": 0.85,
        "Canada": 0.95,
        "India": 0.3,
        "Australia": 1.1,
        "Germany": 0.9,
        "France": 0.8,
        "Japan": 1.05,
        "Singapore": 1.15,
        "China": 0.4,
        "Brazil": 0.35,
        "Mexico": 0.25,
        "Netherlands": 0.95,
        "Sweden": 1.0,
        "Ireland": 0.9,
    }
    
    base = base_salaries.get(job_title, 100000)
    multiplier = country_multipliers.get(country, 1.0)
    variation = random.randint(-20000, 20000)
    
    return max(30000, int(base * multiplier + variation))

def seed_employees(batch_size=1000):
    """Seed database with 10,000 employees"""
    app = create_app()
    
    with app.app_context():
        print("Starting employee seeding...")
        start_time = time.time()
        
        # Clear existing data
        Employee.query.delete()
        db.session.commit()
        
        employees = []
        total_employees = 10000
        
        # Generate employee data
        print(f"Generating {total_employees} employee records...")
        for i in range(total_employees):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"
            
            job_title = random.choice(JOB_TITLES)
            country = random.choice(COUNTRIES)
            salary = generate_salary(job_title, country)
            
            hire_date = datetime.now() - timedelta(days=random.randint(0, 3650))
            
            employee = Employee(
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                job_title=job_title,
                country=country,
                salary=salary,
                department=random.choice(DEPARTMENTS),
                email=f"{first_name.lower()}.{last_name.lower()}{i}@company.com",
                phone=f"+1-555-{random.randint(1000, 9999)}",
                hire_date=hire_date,
                is_active=random.choice([True, True, True, False]),  # 75% active
            )
            
            employees.append(employee)
            
            # Batch insert
            if len(employees) % batch_size == 0:
                print(f"Inserting batch of {batch_size} employees... ({len(employees)}/{total_employees})")
                db.session.bulk_save_objects(employees)
                db.session.commit()
                employees = []
        
        # Insert remaining employees
        if employees:
            print(f"Inserting final batch of {len(employees)} employees...")
            db.session.bulk_save_objects(employees)
            db.session.commit()
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ Seeding complete!")
        print(f"Total employees created: {total_employees}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print(f"Average time per employee: {(elapsed_time/total_employees)*1000:.2f}ms")

if __name__ == '__main__':
    seed_employees()
