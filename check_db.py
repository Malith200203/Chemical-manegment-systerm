#!/usr/bin/env python3
"""
Diagnostic script to check database and test login
"""

import database as db
from werkzeug.security import check_password_hash

print("="*60)
print("DATABASE DIAGNOSTIC")
print("="*60)

# Check if database exists
import os
if not os.path.exists(db.DATABASE_NAME):
    print("\n❌ Database file does NOT exist!")
    print(f"Expected location: {db.DATABASE_NAME}")
    print("\nPlease run: python3 reset_database.py")
    exit(1)

print(f"\n✓ Database file exists: {db.DATABASE_NAME}")

# Check users table
try:
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT id, username, email, full_name, role FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("\n❌ No users found in database!")
        print("Please run: python3 reset_database.py")
    else:
        print(f"\n✓ Found {len(users)} users:")
        print("-" * 60)
        for user in users:
            print(f"  ID: {user['id']} | Username: {user['username']} | Role: {user['role']}")
            print(f"       Email: {user['email']} | Name: {user['full_name']}")
        print("-" * 60)
    
    # Test login for dulsara
    print("\n" + "="*60)
    print("TESTING LOGIN: dulsara / 4321")
    print("="*60)
    
    test_user = db.get_user_by_username('dulsara')
    if test_user:
        print(f"\n✓ User 'dulsara' found in database")
        print(f"  Full name: {test_user['full_name']}")
        print(f"  Email: {test_user['email']}")
        print(f"  Role: {test_user['role']}")
        print(f"  Active: {test_user['is_active']}")
        
        # Test password
        if check_password_hash(test_user['password_hash'], '4321'):
            print("\n✅ PASSWORD VERIFICATION: SUCCESS!")
            print("   Login should work with: dulsara / 4321")
        else:
            print("\n❌ PASSWORD VERIFICATION: FAILED!")
            print("   The password hash doesn't match '4321'")
            
            # Try to show what's stored
            print(f"\n   Stored hash: {test_user['password_hash'][:50]}...")
    else:
        print("\n❌ User 'dulsara' NOT found in database")
        print("   Please run: python3 reset_database.py")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error checking database: {e}")
    print("\nThe database might be corrupted or have an old schema.")
    print("Please run: python3 reset_database.py")

print("\n" + "="*60)
