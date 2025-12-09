#!/usr/bin/env python3
"""
Script to reset and reinitialize the database
WARNING: This will delete all existing data!
"""

import os
import database as db
from werkzeug.security import generate_password_hash

def reset_database():
    """Delete existing database and create a new one"""
    
    # Delete existing database if it exists
    if os.path.exists(db.DATABASE_NAME):
        print(f"Deleting existing database: {db.DATABASE_NAME}")
        os.remove(db.DATABASE_NAME)
        print("✓ Old database deleted")
    
    # Initialize new database
    print("\nInitializing new database...")
    db.init_database()
    print("✓ Database tables created")
    
    # Add sample users
    print("\nAdding users...")
    
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
    
    for user in users_to_add:
        try:
            password_hash = generate_password_hash(user['password'])
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
            print(f"  ✓ Created {user['role']}: {user['username']}")
        except Exception as e:
            print(f"  ✗ Error creating user '{user['username']}': {e}")
    
    print("\n" + "="*60)
    print("Database reset complete!")
    print("="*60)
    print("\nLogin credentials:")
    print("-" * 60)
    print("ADMINS:")
    print("  Username: admin1     | Password: Admin123!")
    print("  Username: admin2     | Password: Admin456!")
    print("  Username: dulsara    | Password: 4321")
    print("\nSTUDENTS:")
    print("  Username: student1   | Password: Student123!")
    print("  Username: student2   | Password: Student456!")
    print("-" * 60)

if __name__ == '__main__':
    print("="*60)
    print("DATABASE RESET UTILITY")
    print("="*60)
    print("\nWARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        reset_database()
    else:
        print("\nOperation cancelled.")
