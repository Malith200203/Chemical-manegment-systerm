#!/usr/bin/env python3
"""
Database initialization script for the Chemical Management System
Run this script to create and initialize the database
"""

from database import init_database

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print("\nDatabase setup complete!")
    print("You can now run the application with: python app.py")
