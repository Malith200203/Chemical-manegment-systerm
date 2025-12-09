#!/usr/bin/env python3
"""
Initialize default users for the Chemical Management System
"""

from werkzeug.security import generate_password_hash
import database as db

def init_default_users():
    """Create default admin and sample student accounts"""
    
    # Ensure database is initialized
    db.init_database()
    
    print("\n" + "="*60)
    print("Initializing Default Users")
    print("="*60 + "\n")
    
    # Check if admin already exists
    existing_admin = db.get_user_by_username('admin')
    
    if not existing_admin:
        # Create default admin account
        admin_password = generate_password_hash('admin123')
        admin_id = db.create_user(
            username='admin',
            email='admin@chemlab.edu',
            password_hash=admin_password,
            full_name='System Administrator',
            role='admin',
            department='Administration',
            phone_number='+1234567890'
        )
        print(f"✓ Default admin account created")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"  Email: admin@chemlab.edu")
        print(f"  ⚠️  Please change the password after first login!\n")
    else:
        print("✓ Admin account already exists\n")
    
    # Create sample student accounts for testing
    sample_students = [
        {
            'username': 'student1',
            'email': 'john.doe@students.edu',
            'password': 'student123',
            'full_name': 'John Doe',
            'student_id': 'STU001',
            'department': 'Chemistry',
            'phone_number': '+1234567891'
        },
        {
            'username': 'student2',
            'email': 'jane.smith@students.edu',
            'password': 'student123',
            'full_name': 'Jane Smith',
            'student_id': 'STU002',
            'department': 'Biology',
            'phone_number': '+1234567892'
        }
    ]
    
    for student in sample_students:
        existing = db.get_user_by_username(student['username'])
        if not existing:
            password_hash = generate_password_hash(student['password'])
            db.create_user(
                username=student['username'],
                email=student['email'],
                password_hash=password_hash,
                full_name=student['full_name'],
                role='student',
                student_id=student['student_id'],
                department=student['department'],
                phone_number=student['phone_number']
            )
            print(f"✓ Sample student account created: {student['username']}")
            print(f"  Email: {student['email']}")
            print(f"  Password: {student['password']}")
            print(f"  Student ID: {student['student_id']}\n")
    
    print("="*60)
    print("User initialization complete!")
    print("="*60 + "\n")

if __name__ == '__main__':
    init_default_users()
