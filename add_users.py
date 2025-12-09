#!/usr/bin/env python3
"""
Script to add sample users to the Chemical Management System
"""

from werkzeug.security import generate_password_hash
import database as db

def add_sample_users():
    """Add 2 admin users and 2 student users"""
    
    # Ensure database exists
    if not db.os.path.exists(db.DATABASE_NAME):
        db.init_database()
    
    users_to_add = [
        # Admins
        {
            'username': 'admin1',
            'email': 'admin1@university.edu',
            'password': 'Admin123!',
            'full_name': 'Dr. Sarah Johnson',
            'role': 'admin',
            'department': 'Chemistry',
            'phone_number': '+1-555-0101'
        },
        {
            'username': 'admin2',
            'email': 'admin2@university.edu',
            'password': 'Admin456!',
            'full_name': 'Dr. Michael Chen',
            'role': 'admin',
            'department': 'Chemical Engineering',
            'phone_number': '+1-555-0102'
        },
        {
            'username': 'dulsara',
            'email': 'dulsara@university.edu',
            'password': '4321',
            'full_name': 'Dulsara',
            'role': 'admin',
            'department': 'Administration',
            'phone_number': '+1-555-0103'
        },
        # Students
        {
            'username': 'student1',
            'email': 'student1@university.edu',
            'password': 'Student123!',
            'full_name': 'Emily Rodriguez',
            'role': 'student',
            'student_id': 'STU001',
            'department': 'Chemistry',
            'phone_number': '+1-555-0201'
        },
        {
            'username': 'student2',
            'email': 'student2@university.edu',
            'password': 'Student456!',
            'full_name': 'James Wilson',
            'role': 'student',
            'student_id': 'STU002',
            'department': 'Biochemistry',
            'phone_number': '+1-555-0202'
        }
    ]
    
    print("Adding users to the database...\n")
    
    for user in users_to_add:
        try:
            # Check if user already exists
            existing_user = db.get_user_by_username(user['username'])
            if existing_user:
                print(f"⚠️  User '{user['username']}' already exists, skipping...")
                continue
            
            # Hash the password
            password_hash = generate_password_hash(user['password'])
            
            # Create the user
            user_id = db.create_user(
                username=user['username'],
                email=user['email'],
                password_hash=password_hash,
                full_name=user['full_name'],
                role=user['role'],
                student_id=user.get('student_id'),
                department=user.get('department'),
                phone_number=user.get('phone_number')
            )
            
            print(f"✓ Created {user['role']}: {user['full_name']} ({user['username']})")
            print(f"  Email: {user['email']}")
            print(f"  Password: {user['password']}")
            if user.get('student_id'):
                print(f"  Student ID: {user['student_id']}")
            print()
            
        except Exception as e:
            print(f"✗ Error creating user '{user['username']}': {e}\n")
    
    print("\n" + "="*60)
    print("User creation complete!")
    print("="*60)
    print("\nLogin credentials summary:")
    print("-" * 60)
    print("\nADMINS:")
    print("  Username: admin1     | Password: Admin123!")
    print("  Username: admin2     | Password: Admin456!")
    print("  Username: dulsara    | Password: 4321")
    print("\nSTUDENTS:")
    print("  Username: student1   | Password: Student123!")
    print("  Username: student2   | Password: Student456!")
    print("-" * 60)

if __name__ == '__main__':
    add_sample_users()
