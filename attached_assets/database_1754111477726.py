import sqlite3
import os

DB_PATH = "data/aura.db"

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Core Tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Properties (
            property_id INTEGER PRIMARY KEY AUTOINCREMENT,
            building TEXT NOT NULL,
            unit TEXT NOT NULL,
            floor INTEGER,
            view TEXT,
            size_sqft REAL,
            bedrooms INTEGER,
            layout_type TEXT,
            UNIQUE(building, unit)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Contacts (
            contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            status TEXT CHECK(status IN ('Hot', 'Warm', 'Cold')) DEFAULT 'Cold',
            last_contacted_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Deals (
            deal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            contact_id INTEGER,
            transaction_type TEXT,
            status TEXT,
            FOREIGN KEY (property_id) REFERENCES Properties (property_id),
            FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            due_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')

    # Intelligence Tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS HistoricalTransactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            sale_price_aed REAL NOT NULL,
            sale_date TEXT NOT NULL,
            agent TEXT,
            source TEXT,
            FOREIGN KEY (property_id) REFERENCES Properties (property_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MasterOwners (
            master_id INTEGER PRIMARY KEY AUTOINCREMENT,
            building TEXT NOT NULL,
            unit_range TEXT,
            owner_name TEXT,
            source_file TEXT,
            confidence_score REAL DEFAULT 0.0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS KnowledgeNexus (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            source_type TEXT,
            embedding_vector BLOB
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DataUploads (
            upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_date TEXT,
            status TEXT,
            purpose TEXT
        )
    ''')
    
    # Junction Table for Many-to-Many relationship between Contacts and Properties
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ContactProperties (
            contact_id INTEGER,
            property_id INTEGER,
            role TEXT,  -- e.g., 'Owner', 'Buyer', 'Tenant'
            FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id),
            FOREIGN KEY (property_id) REFERENCES Properties (property_id),
            PRIMARY KEY (contact_id, property_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS EmailTemplates (
            template_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            subject TEXT NOT NULL,
            body TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_db()
