#!/usr/bin/env python3
"""
Flask application for Laboratory Chemical Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import database as db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
CORS(app)

# Ensure database exists
if not os.path.exists(db.DATABASE_NAME):
    db.init_database()

@app.route('/')
def index():
    """Home page with dashboard"""
    summary = db.get_inventory_summary()
    recent_chemicals = db.get_all_chemicals()[:5]  # Get 5 most recent
    return render_template('index.html', summary=summary, recent_chemicals=recent_chemicals)

@app.route('/inventory')
def inventory():
    """Inventory page showing all chemicals"""
    chemicals = db.get_all_chemicals()
    return render_template('inventory.html', chemicals=chemicals)

@app.route('/chemical/<int:chemical_id>')
def chemical_detail(chemical_id):
    """Chemical detail page"""
    chemical = db.get_chemical_by_id(chemical_id)
    if not chemical:
        return "Chemical not found", 404
    inventory_items = db.get_inventory_for_chemical(chemical_id)
    return render_template('chemical_detail.html', chemical=chemical, inventory_items=inventory_items)

@app.route('/add-chemical')
def add_chemical_page():
    """Add chemical page"""
    hazard_categories = db.get_all_hazard_categories()
    storage_locations = db.get_all_storage_locations()
    return render_template('add_chemical.html', 
                         hazard_categories=hazard_categories, 
                         storage_locations=storage_locations)

@app.route('/edit-chemical/<int:chemical_id>')
def edit_chemical_page(chemical_id):
    """Edit chemical page"""
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
def api_add_chemical():
    """Add a new chemical"""
    data = request.json
    try:
        chemical_id = db.add_chemical(data)
        return jsonify({'success': True, 'id': chemical_id, 'message': 'Chemical added successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chemicals/<int:chemical_id>', methods=['PUT'])
def api_update_chemical(chemical_id):
    """Update a chemical"""
    data = request.json
    try:
        db.update_chemical(chemical_id, data)
        return jsonify({'success': True, 'message': 'Chemical updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chemicals/<int:chemical_id>', methods=['DELETE'])
def api_delete_chemical(chemical_id):
    """Delete a chemical"""
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
def api_add_inventory():
    """Add inventory item"""
    data = request.json
    try:
        item_id = db.add_inventory_item(data)
        return jsonify({'success': True, 'id': item_id, 'message': 'Inventory item added successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/inventory/<int:inventory_id>', methods=['PUT'])
def api_update_inventory(inventory_id):
    """Update inventory quantity"""
    data = request.json
    try:
        db.update_inventory_quantity(inventory_id, data.get('quantity'))
        return jsonify({'success': True, 'message': 'Inventory updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/inventory/<int:inventory_id>', methods=['DELETE'])
def api_delete_inventory(inventory_id):
    """Delete inventory item"""
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

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Laboratory Chemical Management System")
    print("="*60)
    print("\nServer starting...")
    print("Access the application at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
