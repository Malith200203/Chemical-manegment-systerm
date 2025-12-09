#!/usr/bin/env python3
"""
Flask application for Laboratory Chemical Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import database as db
import auth
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
CORS(app)

# Ensure database exists
if not os.path.exists(db.DATABASE_NAME):
    db.init_database()

# Context processor to inject current user into all templates
@app.context_processor
def inject_user():
    """Make current user available to all templates"""
    current_user = auth.get_current_user()
    unread_count = 0
    if current_user:
        unread_count = db.get_unread_count(current_user['id'])
    return dict(current_user=current_user, unread_count=unread_count)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Try to find user by username or email
        user = db.get_user_by_username(username)
        if not user:
            user = db.get_user_by_email(username)
        
        if user and check_password_hash(user['password_hash'], password):
            if user['is_active']:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                if remember:
                    session.permanent = True
                
                # Update last login
                db.update_last_login(user['id'])
                
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration page and handler"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        student_id = request.form.get('student_id')
        department = request.form.get('department')
        phone_number = request.form.get('phone_number')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        if db.get_user_by_username(username):
            flash('Username already exists!', 'danger')
            return render_template('register.html')
        
        if db.get_user_by_email(email):
            flash('Email already registered!', 'danger')
            return render_template('register.html')
        
        # Create user
        try:
            password_hash = generate_password_hash(password)
            user_id = db.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role='student',
                student_id=student_id,
                department=department,
                phone_number=phone_number
            )
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@auth.login_required
def index():
    """Home page with dashboard"""
    current_user = auth.get_current_user()
    summary = db.get_inventory_summary()
    recent_chemicals = db.get_all_chemicals()[:5]  # Get 5 most recent
    
    # Add role-specific data
    if current_user['role'] == 'admin':
        pending_requests = db.get_all_requests('pending')
        borrowed_items = db.get_borrowed_items()
        
        # Count overdue items
        overdue_count = sum(1 for item in borrowed_items 
                          if item['expected_return_date'] and 
                          datetime.strptime(item['expected_return_date'], '%Y-%m-%d').date() < datetime.now().date())
        
        return render_template('index.html', 
                             summary=summary, 
                             recent_chemicals=recent_chemicals,
                             pending_requests_count=len(pending_requests),
                             active_borrows_count=len(borrowed_items),
                             overdue_count=overdue_count)
    else:
        # Student dashboard
        my_requests = db.get_requests_by_student(current_user['id'])
        my_borrowed = db.get_borrowed_items(current_user['id'])
        pending_count = sum(1 for r in my_requests if r['status'] == 'pending')
        
        return render_template('index.html', 
                             summary=summary, 
                             recent_chemicals=recent_chemicals,
                             my_requests_count=len(my_requests),
                             my_borrowed_count=len(my_borrowed),
                             pending_count=pending_count)

@app.route('/inventory')
@auth.login_required
def inventory():
    """Inventory page showing all chemicals"""
    chemicals = db.get_all_chemicals()
    return render_template('inventory.html', chemicals=chemicals)

@app.route('/chemical/<int:chemical_id>')
@auth.login_required
def chemical_detail(chemical_id):
    """Chemical detail page"""
    chemical = db.get_chemical_by_id(chemical_id)
    if not chemical:
        return "Chemical not found", 404
    inventory_items = db.get_inventory_for_chemical(chemical_id)
    available = db.get_available_quantity(chemical_id)
    return render_template('chemical_detail.html', 
                         chemical=chemical, 
                         inventory_items=inventory_items,
                         available=available)

@app.route('/add-chemical')
@auth.admin_required
def add_chemical_page():
    """Add chemical page - Admin only"""
    hazard_categories = db.get_all_hazard_categories()
    storage_locations = db.get_all_storage_locations()
    return render_template('add_chemical.html', 
                         hazard_categories=hazard_categories, 
                         storage_locations=storage_locations)

@app.route('/edit-chemical/<int:chemical_id>')
@auth.admin_required
def edit_chemical_page(chemical_id):
    """Edit chemical page - Admin only"""
    chemical = db.get_chemical_by_id(chemical_id)
    if not chemical:
        return "Chemical not found", 404
    hazard_categories = db.get_all_hazard_categories()
    storage_locations = db.get_all_storage_locations()
    return render_template('edit_chemical.html', 
                         chemical=chemical,
                         hazard_categories=hazard_categories, 
                         storage_locations=storage_locations)

# API Endpoints

@app.route('/api/chemicals', methods=['GET'])
def api_get_chemicals():
    """Get all chemicals"""
    chemicals = db.get_all_chemicals()
    return jsonify([dict(c) for c in chemicals])

@app.route('/api/chemicals/<int:chemical_id>', methods=['GET'])
def api_get_chemical(chemical_id):
    """Get a specific chemical"""
    chemical = db.get_chemical_by_id(chemical_id)
    if not chemical:
        return jsonify({'error': 'Chemical not found'}), 404
    return jsonify(dict(chemical))

@app.route('/api/chemicals', methods=['POST'])
@auth.admin_required
def api_add_chemical():
    """Add a new chemical - Admin only"""
    data = request.json
    try:
        chemical_id = db.add_chemical(data)
        return jsonify({'success': True, 'id': chemical_id, 'message': 'Chemical added successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chemicals/<int:chemical_id>', methods=['PUT'])
@auth.admin_required
def api_update_chemical(chemical_id):
    """Update a chemical - Admin only"""
    data = request.json
    try:
        db.update_chemical(chemical_id, data)
        return jsonify({'success': True, 'message': 'Chemical updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chemicals/<int:chemical_id>', methods=['DELETE'])
@auth.admin_required
def api_delete_chemical(chemical_id):
    """Delete a chemical - Admin only"""
    try:
        db.delete_chemical(chemical_id)
        return jsonify({'success': True, 'message': 'Chemical deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/inventory', methods=['GET'])
def api_get_inventory():
    """Get inventory summary"""
    summary = db.get_inventory_summary()
    return jsonify(dict(summary))

@app.route('/api/inventory/<int:chemical_id>', methods=['GET'])
def api_get_chemical_inventory(chemical_id):
    """Get inventory for a specific chemical"""
    inventory = db.get_inventory_for_chemical(chemical_id)
    return jsonify([dict(i) for i in inventory])

@app.route('/api/inventory', methods=['POST'])
@auth.admin_required
def api_add_inventory():
    """Add inventory item - Admin only"""
    data = request.json
    try:
        item_id = db.add_inventory_item(data)
        return jsonify({'success': True, 'id': item_id, 'message': 'Inventory item added successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/inventory/<int:inventory_id>', methods=['PUT'])
@auth.admin_required
def api_update_inventory(inventory_id):
    """Update inventory quantity - Admin only"""
    data = request.json
    try:
        db.update_inventory_quantity(inventory_id, data.get('quantity'))
        return jsonify({'success': True, 'message': 'Inventory updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/inventory/<int:inventory_id>', methods=['DELETE'])
@auth.admin_required
def api_delete_inventory(inventory_id):
    """Delete inventory item - Admin only"""
    try:
        db.delete_inventory_item(inventory_id)
        return jsonify({'success': True, 'message': 'Inventory item deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/locations', methods=['GET'])
def api_get_locations():
    """Get all storage locations"""
    locations = db.get_all_storage_locations()
    return jsonify([dict(l) for l in locations])

@app.route('/api/hazards', methods=['GET'])
def api_get_hazards():
    """Get all hazard categories"""
    hazards = db.get_all_hazard_categories()
    return jsonify([dict(h) for h in hazards])

@app.route('/api/search', methods=['GET'])
def api_search():
    """Search chemicals"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    chemicals = db.search_chemicals(query)
    return jsonify([dict(c) for c in chemicals])

# Student routes
@app.route('/student/request-chemical/<int:chemical_id>', methods=['GET', 'POST'])
@auth.student_required
def request_chemical(chemical_id):
    """Student request chemical page"""
    chemical = db.get_chemical_by_id(chemical_id)
    if not chemical:
        flash('Chemical not found', 'danger')
        return redirect(url_for('inventory'))
    
    if request.method == 'POST':
        current_user = auth.get_current_user()
        quantity = float(request.form.get('quantity'))
        unit = request.form.get('unit')
        purpose = request.form.get('purpose')
        required_date = request.form.get('required_date')
        expected_return_date = request.form.get('expected_return_date')
        
        # Check available quantity
        available = db.get_available_quantity(chemical_id)
        if quantity > (available['total_quantity'] - available['borrowed_quantity']):
            flash('Requested quantity exceeds available stock!', 'danger')
            return redirect(request.url)
        
        try:
            request_id = db.create_request(
                student_id=current_user['id'],
                chemical_id=chemical_id,
                quantity_requested=quantity,
                unit=unit,
                purpose=purpose,
                required_date=required_date,
                expected_return_date=expected_return_date
            )
            
            # Notify admins
            admins = [u for u in db.get_all_users() if u['role'] == 'admin']
            for admin in admins:
                db.create_notification(
                    user_id=admin['id'],
                    title='New Chemical Request',
                    message=f'{current_user["full_name"]} requested {quantity} {unit} of {chemical["name"]}',
                    notification_type='request',
                    related_entity_type='request',
                    related_entity_id=request_id
                )
            
            flash('Request submitted successfully!', 'success')
            return redirect(url_for('my_requests'))
        except Exception as e:
            flash(f'Error submitting request: {str(e)}', 'danger')
    
    available = db.get_available_quantity(chemical_id)
    inventory_items = db.get_inventory_for_chemical(chemical_id)
    return render_template('student_request.html', 
                         chemical=chemical, 
                         available=available,
                         inventory_items=inventory_items)

@app.route('/student/my-requests')
@auth.student_required
def my_requests():
    """Student view their requests"""
    current_user = auth.get_current_user()
    requests = db.get_requests_by_student(current_user['id'])
    return render_template('student_requests.html', requests=requests)

@app.route('/student/my-borrowed')
@auth.student_required
def my_borrowed():
    """Student view their borrowed items"""
    current_user = auth.get_current_user()
    borrowed_items = db.get_borrowed_items(current_user['id'])
    return render_template('student_borrowed.html', borrowed_items=borrowed_items)

# Admin routes
@app.route('/admin/requests')
@auth.admin_required
def admin_requests():
    """Admin view all requests"""
    status_filter = request.args.get('status', 'pending')
    requests = db.get_all_requests(status_filter if status_filter != 'all' else None)
    return render_template('admin_requests.html', requests=requests, status_filter=status_filter)

@app.route('/admin/borrowed')
@auth.admin_required
def admin_borrowed():
    """Admin view all borrowed items"""
    borrowed_items = db.get_borrowed_items()
    return render_template('admin_borrowed.html', borrowed_items=borrowed_items)

@app.route('/admin/users')
@auth.admin_required
def admin_users():
    """Admin view all users"""
    users = db.get_all_users()
    return render_template('admin_users.html', users=users)

@app.route('/profile', methods=['GET', 'POST'])
@auth.login_required
def profile():
    """User profile page"""
    current_user = auth.get_current_user()
    
    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name'),
            'department': request.form.get('department'),
            'phone_number': request.form.get('phone_number'),
            'student_id': request.form.get('student_id')
        }
        
        try:
            db.update_user(current_user['id'], data)
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('profile.html', user=current_user)

@app.route('/notifications')
@auth.login_required
def notifications():
    """View notifications"""
    current_user = auth.get_current_user()
    user_notifications = db.get_user_notifications(current_user['id'])
    return render_template('notifications.html', notifications=user_notifications)

# API endpoints for requests
@app.route('/api/requests', methods=['POST'])
@auth.student_required
def api_create_request():
    """Create new chemical request"""
    current_user = auth.get_current_user()
    data = request.json
    
    try:
        # Check available quantity
        available = db.get_available_quantity(data['chemical_id'])
        if data['quantity_requested'] > (available['total_quantity'] - available['borrowed_quantity']):
            return jsonify({'success': False, 'error': 'Requested quantity exceeds available stock'}), 400
        
        request_id = db.create_request(
            student_id=current_user['id'],
            chemical_id=data['chemical_id'],
            quantity_requested=data['quantity_requested'],
            unit=data['unit'],
            purpose=data['purpose'],
            required_date=data['required_date'],
            expected_return_date=data['expected_return_date']
        )
        
        return jsonify({'success': True, 'id': request_id, 'message': 'Request created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/requests', methods=['GET'])
@auth.login_required
def api_get_requests():
    """Get requests (all for admin, own for student)"""
    current_user = auth.get_current_user()
    
    if current_user['role'] == 'admin':
        status = request.args.get('status')
        requests = db.get_all_requests(status)
    else:
        requests = db.get_requests_by_student(current_user['id'])
    
    return jsonify([dict(r) for r in requests])

@app.route('/api/requests/<int:request_id>', methods=['GET'])
@auth.login_required
def api_get_request(request_id):
    """Get request details"""
    req = db.get_request_by_id(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404
    return jsonify(dict(req))

@app.route('/api/requests/<int:request_id>/approve', methods=['PUT'])
@auth.admin_required
def api_approve_request(request_id):
    """Approve a request"""
    current_user = auth.get_current_user()
    data = request.json
    
    try:
        db.approve_request(request_id, current_user['id'], data.get('admin_notes'))
        
        # Notify student
        req = db.get_request_by_id(request_id)
        db.create_notification(
            user_id=req['student_id'],
            title='Request Approved',
            message=f'Your request for {req["chemical_name"]} has been approved',
            notification_type='approval',
            related_entity_type='request',
            related_entity_id=request_id
        )
        
        return jsonify({'success': True, 'message': 'Request approved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/requests/<int:request_id>/reject', methods=['PUT'])
@auth.admin_required
def api_reject_request(request_id):
    """Reject a request"""
    current_user = auth.get_current_user()
    data = request.json
    
    try:
        db.reject_request(request_id, current_user['id'], data.get('rejection_reason', 'No reason provided'))
        
        # Notify student
        req = db.get_request_by_id(request_id)
        db.create_notification(
            user_id=req['student_id'],
            title='Request Rejected',
            message=f'Your request for {req["chemical_name"]} has been rejected',
            notification_type='rejection',
            related_entity_type='request',
            related_entity_id=request_id
        )
        
        return jsonify({'success': True, 'message': 'Request rejected successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/requests/<int:request_id>/mark-borrowed', methods=['PUT'])
@auth.admin_required
def api_mark_borrowed(request_id):
    """Mark request as borrowed"""
    data = request.json
    
    try:
        db.mark_as_borrowed(
            request_id=request_id,
            inventory_id=data.get('inventory_id'),
            condition_at_borrow=data.get('condition_at_borrow', 'Good'),
            notes=data.get('notes')
        )
        
        # Notify student
        req = db.get_request_by_id(request_id)
        db.create_notification(
            user_id=req['student_id'],
            title='Item Ready for Pickup',
            message=f'{req["chemical_name"]} is ready for pickup',
            notification_type='borrow',
            related_entity_type='request',
            related_entity_id=request_id
        )
        
        return jsonify({'success': True, 'message': 'Marked as borrowed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/requests/<int:request_id>/mark-returned', methods=['PUT'])
@auth.admin_required
def api_mark_returned(request_id):
    """Mark borrowed item as returned"""
    data = request.json
    
    try:
        db.mark_as_returned(
            request_id=request_id,
            condition_at_return=data.get('condition_at_return', 'Good'),
            notes=data.get('notes')
        )
        
        # Notify student
        req = db.get_request_by_id(request_id)
        db.create_notification(
            user_id=req['student_id'],
            title='Return Confirmed',
            message=f'Return of {req["chemical_name"]} has been confirmed',
            notification_type='return',
            related_entity_type='request',
            related_entity_id=request_id
        )
        
        return jsonify({'success': True, 'message': 'Marked as returned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/borrowed', methods=['GET'])
@auth.login_required
def api_get_borrowed():
    """Get borrowed items"""
    current_user = auth.get_current_user()
    
    if current_user['role'] == 'admin':
        items = db.get_borrowed_items()
    else:
        items = db.get_borrowed_items(current_user['id'])
    
    return jsonify([dict(i) for i in items])

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@auth.login_required
def api_mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        db.mark_notification_as_read(notification_id)
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Laboratory Chemical Management System")
    print("="*60)
    print("\nServer starting...")
    print("Access the application at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
