import sqlite3
import os
from datetime import datetime

DATABASE_NAME = 'chemical_management.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create hazard_categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hazard_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            color_code TEXT
        )
    ''')
    
    # Create storage_locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS storage_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            building TEXT,
            room TEXT,
            cabinet TEXT,
            shelf TEXT,
            capacity_liters REAL,
            current_usage REAL DEFAULT 0
        )
    ''')
    
    # Create chemicals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chemicals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            chemical_formula TEXT,
            cas_number TEXT UNIQUE,
            molecular_weight REAL,
            description TEXT,
            supplier TEXT,
            hazard_category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hazard_category_id) REFERENCES hazard_categories(id)
        )
    ''')
    
    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            storage_location_id INTEGER,
            batch_number TEXT,
            expiry_date DATE,
            received_date DATE,
            cost REAL,
            notes TEXT,
            FOREIGN KEY (chemical_id) REFERENCES chemicals(id) ON DELETE CASCADE,
            FOREIGN KEY (storage_location_id) REFERENCES storage_locations(id)
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create activity_log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    
    # Insert default hazard categories
    try:
        hazard_categories = [
            ('Flammable', 'Easily ignitable substances', '#FF4444'),
            ('Toxic', 'Poisonous substances', '#9B59B6'),
            ('Corrosive', 'Substances that cause burns', '#F39C12'),
            ('Oxidizing', 'Substances that may cause or intensify fire', '#E74C3C'),
            ('Explosive', 'Substances that may explode', '#C0392B'),
            ('Irritant', 'Substances causing irritation', '#3498DB'),
            ('Carcinogenic', 'Cancer-causing substances', '#8E44AD'),
            ('Environmental Hazard', 'Harmful to environment', '#27AE60')
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO hazard_categories (name, description, color_code) VALUES (?, ?, ?)',
            hazard_categories
        )
        
        # Insert default storage locations
        storage_locations = [
            ('Main Lab', 'Building A', 'Lab 101', 'Cabinet 1', 'Shelf A', 100.0),
            ('Main Lab', 'Building A', 'Lab 101', 'Cabinet 1', 'Shelf B', 100.0),
            ('Main Lab', 'Building A', 'Lab 101', 'Cabinet 2', 'Shelf A', 100.0),
            ('Cold Storage', 'Building A', 'Lab 102', 'Refrigerator 1', 'Shelf 1', 50.0),
            ('Acid Storage', 'Building A', 'Lab 103', 'Acid Cabinet', 'Shelf A', 75.0),
            ('Flammable Storage', 'Building B', 'Storage Room', 'Flammable Cabinet', 'Shelf 1', 150.0)
        ]
        
        cursor.executemany(
            '''INSERT OR IGNORE INTO storage_locations 
               (location_name, building, room, cabinet, shelf, capacity_liters) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            storage_locations
        )
        
        # Insert sample chemicals
        sample_chemicals = [
            ('Hydrochloric Acid', 'HCl', '7647-01-0', 36.46, 'Strong acid, corrosive', 'Sigma-Aldrich', 3),
            ('Sodium Hydroxide', 'NaOH', '1310-73-2', 40.00, 'Strong base, corrosive', 'Fisher Scientific', 3),
            ('Ethanol', 'C2H5OH', '64-17-5', 46.07, 'Flammable liquid', 'Merck', 1),
            ('Acetone', 'C3H6O', '67-64-1', 58.08, 'Flammable solvent', 'Sigma-Aldrich', 1),
            ('Sulfuric Acid', 'H2SO4', '7664-93-9', 98.08, 'Highly corrosive acid', 'Fisher Scientific', 3),
            ('Sodium Chloride', 'NaCl', '7647-14-5', 58.44, 'Common salt', 'Merck', 6),
            ('Methanol', 'CH3OH', '67-56-1', 32.04, 'Toxic flammable liquid', 'Sigma-Aldrich', 2),
            ('Benzene', 'C6H6', '71-43-2', 78.11, 'Carcinogenic aromatic hydrocarbon', 'Merck', 7)
        ]
        
        cursor.executemany(
            '''INSERT OR IGNORE INTO chemicals 
               (name, chemical_formula, cas_number, molecular_weight, description, supplier, hazard_category_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            sample_chemicals
        )
        
        # Insert sample inventory items
        sample_inventory = [
            (1, 2.5, 'L', 5, 'BATCH-HCL-001', '2025-12-31', '2024-01-15', 45.00, 'Handle with care'),
            (2, 1.0, 'kg', 1, 'BATCH-NAOH-001', '2026-06-30', '2024-02-01', 30.00, 'Store in dry place'),
            (3, 5.0, 'L', 1, 'BATCH-ETH-001', '2025-08-31', '2024-03-10', 75.00, 'Keep away from heat'),
            (4, 2.5, 'L', 6, 'BATCH-ACE-001', '2025-10-31', '2024-03-15', 55.00, 'Flammable storage'),
            (5, 1.0, 'L', 5, 'BATCH-H2SO4-001', '2026-12-31', '2024-01-20', 50.00, 'Extreme caution'),
            (6, 5.0, 'kg', 1, 'BATCH-NACL-001', '2027-12-31', '2024-02-05', 15.00, 'General storage'),
            (7, 1.0, 'L', 6, 'BATCH-METH-001', '2025-07-31', '2024-03-01', 40.00, 'Toxic - keep sealed'),
            (8, 0.5, 'L', 6, 'BATCH-BEN-001', '2025-09-30', '2024-03-20', 65.00, 'Carcinogenic - special handling')
        ]
        
        cursor.executemany(
            '''INSERT OR IGNORE INTO inventory 
               (chemical_id, quantity, unit, storage_location_id, batch_number, expiry_date, received_date, cost, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            sample_inventory
        )
        
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Data already exists
    
    conn.close()
    print("Database initialized successfully!")

# Database operation functions
def get_all_chemicals():
    """Get all chemicals with their details"""
    conn = get_db_connection()
    chemicals = conn.execute('''
        SELECT c.*, h.name as hazard_name, h.color_code
        FROM chemicals c
        LEFT JOIN hazard_categories h ON c.hazard_category_id = h.id
        ORDER BY c.name
    ''').fetchall()
    conn.close()
    return chemicals

def get_chemical_by_id(chemical_id):
    """Get a specific chemical by ID"""
    conn = get_db_connection()
    chemical = conn.execute('''
        SELECT c.*, h.name as hazard_name, h.color_code, h.description as hazard_description
        FROM chemicals c
        LEFT JOIN hazard_categories h ON c.hazard_category_id = h.id
        WHERE c.id = ?
    ''', (chemical_id,)).fetchone()
    conn.close()
    return chemical

def get_inventory_for_chemical(chemical_id):
    """Get inventory items for a specific chemical"""
    conn = get_db_connection()
    inventory = conn.execute('''
        SELECT i.*, 
               s.location_name, s.building, s.room, s.cabinet, s.shelf
        FROM inventory i
        LEFT JOIN storage_locations s ON i.storage_location_id = s.id
        WHERE i.chemical_id = ?
    ''', (chemical_id,)).fetchall()
    conn.close()
    return inventory

def add_chemical(data):
    """Add a new chemical"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chemicals 
        (name, chemical_formula, cas_number, molecular_weight, description, supplier, hazard_category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('chemical_formula'),
        data.get('cas_number'),
        data.get('molecular_weight'),
        data.get('description'),
        data.get('supplier'),
        data.get('hazard_category_id')
    ))
    chemical_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chemical_id

def update_chemical(chemical_id, data):
    """Update an existing chemical"""
    conn = get_db_connection()
    conn.execute('''
        UPDATE chemicals 
        SET name = ?, chemical_formula = ?, cas_number = ?, 
            molecular_weight = ?, description = ?, supplier = ?, 
            hazard_category_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        data.get('name'),
        data.get('chemical_formula'),
        data.get('cas_number'),
        data.get('molecular_weight'),
        data.get('description'),
        data.get('supplier'),
        data.get('hazard_category_id'),
        chemical_id
    ))
    conn.commit()
    conn.close()

def delete_chemical(chemical_id):
    """Delete a chemical"""
    conn = get_db_connection()
    conn.execute('DELETE FROM chemicals WHERE id = ?', (chemical_id,))
    conn.commit()
    conn.close()

def get_all_storage_locations():
    """Get all storage locations"""
    conn = get_db_connection()
    locations = conn.execute('SELECT * FROM storage_locations ORDER BY location_name, cabinet, shelf').fetchall()
    conn.close()
    return locations

def get_all_hazard_categories():
    """Get all hazard categories"""
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM hazard_categories ORDER BY name').fetchall()
    conn.close()
    return categories

def get_inventory_summary():
    """Get inventory summary with totals"""
    conn = get_db_connection()
    summary = conn.execute('''
        SELECT 
            COUNT(DISTINCT c.id) as total_chemicals,
            COUNT(i.id) as total_inventory_items,
            SUM(CASE WHEN i.expiry_date < date('now') THEN 1 ELSE 0 END) as expired_items,
            SUM(CASE WHEN i.expiry_date BETWEEN date('now') AND date('now', '+30 days') THEN 1 ELSE 0 END) as expiring_soon
        FROM chemicals c
        LEFT JOIN inventory i ON c.id = i.chemical_id
    ''').fetchone()
    conn.close()
    return summary

def add_inventory_item(data):
    """Add a new inventory item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventory 
        (chemical_id, quantity, unit, storage_location_id, batch_number, expiry_date, received_date, cost, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('chemical_id'),
        data.get('quantity'),
        data.get('unit'),
        data.get('storage_location_id'),
        data.get('batch_number'),
        data.get('expiry_date'),
        data.get('received_date'),
        data.get('cost'),
        data.get('notes')
    ))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def update_inventory_quantity(inventory_id, new_quantity):
    """Update inventory quantity"""
    conn = get_db_connection()
    conn.execute('UPDATE inventory SET quantity = ? WHERE id = ?', (new_quantity, inventory_id))
    conn.commit()
    conn.close()

def delete_inventory_item(inventory_id):
    """Delete an inventory item"""
    conn = get_db_connection()
    conn.execute('DELETE FROM inventory WHERE id = ?', (inventory_id,))
    conn.commit()
    conn.close()

def search_chemicals(query):
    """Search chemicals by name, formula, or CAS number"""
    conn = get_db_connection()
    search_term = f'%{query}%'
    chemicals = conn.execute('''
        SELECT c.*, h.name as hazard_name, h.color_code
        FROM chemicals c
        LEFT JOIN hazard_categories h ON c.hazard_category_id = h.id
        WHERE c.name LIKE ? OR c.chemical_formula LIKE ? OR c.cas_number LIKE ?
        ORDER BY c.name
    ''', (search_term, search_term, search_term)).fetchall()
    conn.close()
    return chemicals
