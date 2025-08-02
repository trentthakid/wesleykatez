import sqlite3
import os
import logging
from datetime import datetime

DATABASE_PATH = 'digital_twin.db'

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Core operational tables
    
    # Properties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            building TEXT NOT NULL,
            unit TEXT NOT NULL,
            area TEXT,
            property_type TEXT,
            bedrooms INTEGER,
            bathrooms INTEGER,
            size_sqft REAL,
            price REAL,
            status TEXT DEFAULT 'Available',
            description TEXT,
            amenities TEXT,
            created_date TEXT,
            updated_date TEXT,
            UNIQUE(building, unit)
        )
    ''')
    
    # Contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            lead_status TEXT DEFAULT 'Cold',
            source TEXT,
            notes TEXT,
            last_contacted_date TEXT,
            created_date TEXT,
            updated_date TEXT
        )
    ''')
    
    # Deals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            contact_id INTEGER,
            deal_type TEXT,
            status TEXT DEFAULT 'Active',
            deal_value REAL,
            commission REAL,
            created_date TEXT,
            closing_date TEXT,
            notes TEXT,
            FOREIGN KEY (property_id) REFERENCES Properties (id),
            FOREIGN KEY (contact_id) REFERENCES Contacts (id)
        )
    ''')
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Medium',
            assigned_to TEXT,
            contact_id INTEGER,
            property_id INTEGER,
            created_date TEXT,
            due_date TEXT,
            completed_date TEXT,
            FOREIGN KEY (contact_id) REFERENCES Contacts (id),
            FOREIGN KEY (property_id) REFERENCES Properties (id)
        )
    ''')
    
    # ContactProperties junction table for many-to-many relationships
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ContactProperties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            property_id INTEGER,
            relationship_type TEXT,
            start_date TEXT,
            end_date TEXT,
            created_date TEXT,
            FOREIGN KEY (contact_id) REFERENCES Contacts (id),
            FOREIGN KEY (property_id) REFERENCES Properties (id),
            UNIQUE(contact_id, property_id, relationship_type)
        )
    ''')
    
    # Intelligence tables for advanced features
    
    # Historical transactions for market analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS HistoricalTransactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            transaction_type TEXT,
            price REAL,
            transaction_date TEXT,
            buyer_name TEXT,
            seller_name TEXT,
            agent_commission REAL,
            market_conditions TEXT,
            created_date TEXT,
            FOREIGN KEY (property_id) REFERENCES Properties (id)
        )
    ''')
    
    # Master owners table for consolidated ownership data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MasterOwners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            owner_name TEXT,
            owner_email TEXT,
            owner_phone TEXT,
            ownership_percentage REAL DEFAULT 100.0,
            confidence_score REAL DEFAULT 1.0,
            data_source TEXT,
            verified BOOLEAN DEFAULT FALSE,
            created_date TEXT,
            updated_date TEXT,
            FOREIGN KEY (property_id) REFERENCES Properties (id)
        )
    ''')
    
    # Knowledge nexus for RAG and semantic search
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS KnowledgeNexus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT,
            title TEXT,
            content TEXT,
            embedding_vector BLOB,
            source_file TEXT,
            metadata TEXT,
            tags TEXT,
            created_date TEXT,
            updated_date TEXT
        )
    ''')
    
    # Email templates for automation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS EmailTemplates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT UNIQUE,
            subject TEXT,
            body TEXT,
            template_type TEXT,
            variables TEXT,
            created_date TEXT,
            updated_date TEXT
        )
    ''')
    
    # Market data for intelligence
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MarketData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT,
            property_type TEXT,
            average_price REAL,
            median_price REAL,
            price_per_sqft REAL,
            total_transactions INTEGER,
            market_trend TEXT,
            data_date TEXT,
            created_date TEXT
        )
    ''')
    
    # Lead scoring data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LeadScores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            score INTEGER,
            score_factors TEXT,
            last_calculated TEXT,
            FOREIGN KEY (contact_id) REFERENCES Contacts (id)
        )
    ''')
    
    conn.commit()
    
    # Insert sample data if tables are empty
    insert_sample_data(cursor, conn)
    
    conn.close()
    logging.info("Database initialized successfully")

def insert_sample_data(cursor, conn):
    """Insert sample data for demonstration"""
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM Properties")
    if cursor.fetchone()[0] > 0:
        return  # Data already exists
    
    # Sample properties
    properties = [
        ('Palm Tower', '3401', 'Palm Jumeirah', 'Apartment', 2, 2, 1200.0, 2500000.0, 'Available', 'Luxury apartment with sea view'),
        ('Marina Residences', '1205', 'Palm Jumeirah', 'Apartment', 3, 3, 1800.0, 3200000.0, 'Available', 'Spacious family apartment'),
        ('Shoreline Apartments', '0804', 'Palm Jumeirah', 'Apartment', 1, 1, 800.0, 1800000.0, 'Sold', 'Cozy beachfront unit'),
        ('Golden Mile', '2106', 'Palm Jumeirah', 'Apartment', 2, 2, 1100.0, 2200000.0, 'Available', 'Modern apartment with amenities'),
        ('Garden Homes', 'Villa A15', 'Palm Jumeirah', 'Villa', 4, 5, 3500.0, 8500000.0, 'Available', 'Luxury beachfront villa'),
    ]
    
    created_date = datetime.now().isoformat()
    for prop in properties:
        cursor.execute('''
            INSERT INTO Properties (building, unit, area, property_type, bedrooms, bathrooms, 
                                  size_sqft, price, status, description, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*prop, created_date, created_date))
    
    # Sample contacts
    contacts = [
        ('Ahmed Al Rashid', 'ahmed.rashid@email.com', '+971-50-123-4567', 'Hot', 'Referral'),
        ('Sarah Johnson', 'sarah.j@email.com', '+971-55-987-6543', 'Warm', 'Website'),
        ('Mohammed Hassan', 'mohammed.h@email.com', '+971-50-555-1234', 'Cold', 'Walk-in'),
        ('Lisa Chen', 'lisa.chen@email.com', '+971-56-777-8888', 'Hot', 'Social Media'),
        ('David Smith', 'david.smith@email.com', '+971-50-999-0000', 'Warm', 'Previous Client'),
    ]
    
    for contact in contacts:
        cursor.execute('''
            INSERT INTO Contacts (name, email, phone, lead_status, source, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (*contact, created_date))
    
    # Sample contact-property relationships
    relationships = [
        (1, 1, 'Owner'),  # Ahmed owns Palm Tower 3401
        (2, 2, 'Interested'),  # Sarah interested in Marina Residences
        (3, 3, 'Previous Owner'),  # Mohammed previously owned Shoreline
        (4, 4, 'Viewing Scheduled'),  # Lisa scheduled viewing for Golden Mile
        (5, 5, 'Owner'),  # David owns Garden Homes villa
    ]
    
    for rel in relationships:
        cursor.execute('''
            INSERT INTO ContactProperties (contact_id, property_id, relationship_type, created_date)
            VALUES (?, ?, ?, ?)
        ''', (*rel, created_date))
    
    # Sample tasks
    tasks = [
        ('Follow up with Ahmed about Palm Tower maintenance', 'Ahmed mentioned some issues with AC', 'Pending', 'High', 1, 1),
        ('Schedule viewing for Sarah', 'Sarah wants to see Marina Residences this week', 'Pending', 'Medium', 2, 2),
        ('Prepare CMA for Golden Mile area', 'Lisa requested market analysis', 'In Progress', 'Medium', 4, None),
        ('Update property photos', 'Garden Homes needs new photography', 'Pending', 'Low', None, 5),
        ('Call David about referrals', 'David might have friends looking for properties', 'Pending', 'Medium', 5, None),
    ]
    
    due_date = (datetime.now()).isoformat()
    for task in tasks:
        cursor.execute('''
            INSERT INTO Tasks (title, description, status, priority, contact_id, property_id, 
                             created_date, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*task, created_date, due_date))
    
    # Sample email templates
    templates = [
        ('follow_up_hot', 'Quick Follow-up', 
         'Hi {name},\n\nI wanted to follow up on your interest in {property}. Do you have any questions or would you like to schedule a viewing?\n\nBest regards,\nYour Real Estate Agent',
         'follow_up'),
        ('welcome_new_lead', 'Welcome to Our Services', 
         'Dear {name},\n\nThank you for your interest in Dubai real estate. I look forward to helping you find your perfect property.\n\nBest regards,\nYour Real Estate Agent',
         'welcome'),
        ('viewing_confirmation', 'Property Viewing Confirmation', 
         'Hi {name},\n\nThis confirms your property viewing for {property} on {date} at {time}.\n\nSee you there!\nYour Real Estate Agent',
         'confirmation'),
    ]
    
    for template in templates:
        cursor.execute('''
            INSERT INTO EmailTemplates (template_name, subject, body, template_type, created_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (*template, created_date))
    
    conn.commit()
    logging.info("Sample data inserted successfully")
