"""
Authentication utilities and decorators for the Chemical Management System
"""

from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import UserMixin
import database as db

class User(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_id, username, email, full_name, role, student_id=None, department=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        self.student_id = student_id
        self.department = department
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'student'
    
    @staticmethod
    def get(user_id):
        """Get user by ID for Flask-Login"""
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(
                user_id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                student_id=user_data.get('student_id'),
                department=user_data.get('department')
            )
        return None

def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = db.get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator to require student role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = db.get_user_by_id(session['user_id'])
        if not user or user['role'] != 'student':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the currently logged in user"""
    if 'user_id' in session:
        return db.get_user_by_id(session['user_id'])
    return None
