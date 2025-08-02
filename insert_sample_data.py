import sqlite3
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Establish a connection to the database"""
    conn = sqlite3.connect('digital_twin.db')
    conn.row_factory = sqlite3.Row
    return conn

def clear_existing_data():
    """Clear existing data from the tables to ensure a clean slate."""
    conn = get_db_connection()
    cursor = conn.cursor()
    tables = ['Properties', 'Contacts', 'Tasks', 'Deals', 'ContactProperties']
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table};")
            logging.info(f"Cleared data from table: {table}")
        except sqlite3.OperationalError as e:
            logging.warning(f"Could not clear table {table} (it might not exist yet): {e}")
    conn.commit()
    conn.close()

def insert_sample_data():
    """Inserts a set of sample data into the database for testing purposes."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # --- Insert Sample Properties ---
        properties = [
            (1, 'Shoreline Apartments', '101', 'Palm Jumeirah', 'Apartment', 2, 3, 1580, 2500000, 'Available', datetime.now().isoformat()),
            (2, 'Garden Homes', 'Villa 42', 'Palm Jumeirah', 'Villa', 4, 5, 5000, 12000000, 'Available', datetime.now().isoformat()),
            (3, 'The Palm Tower', '3401', 'Palm Jumeirah', 'Apartment', 1, 2, 1050, 3500000, 'Sold', datetime.now().isoformat())
        ]
        cursor.executemany("""
            INSERT INTO Properties (id, building, unit, area, property_type, bedrooms, bathrooms, size_sqft, price, status, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, properties)
        logging.info("Inserted 3 sample properties.")

        # --- Insert Sample Contacts ---
        contacts = [
            (1, 'Ahmed Al Futtaim', 'ahmed.f@email.com', '+971501234567', 'Hot', 'AI Assistant', (datetime.now() - timedelta(days=2)).isoformat(), datetime.now().isoformat()),
            (2, 'Fatima Al Habtoor', 'fatima.h@email.com', '+971559876543', 'Warm', 'Referral', (datetime.now() - timedelta(days=10)).isoformat(), datetime.now().isoformat()),
            (3, 'John Smith', 'john.s@email.com', '+442071234567', 'Cold', 'Website', (datetime.now() - timedelta(days=30)).isoformat(), datetime.now().isoformat())
        ]
        cursor.executemany("""
            INSERT INTO Contacts (id, name, email, phone, lead_status, source, last_contacted_date, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, contacts)
        logging.info("Inserted 3 sample contacts.")

        # --- Insert Sample Tasks ---
        tasks = [
            ('Follow up with Ahmed Al Futtaim', 'Discuss the Garden Home on Frond C.', 'Pending', datetime.now().isoformat(), (datetime.now() + timedelta(days=1)).isoformat(), 1),
            ('Prepare CMA for Fatima Al Habtoor', 'She is interested in Shoreline apartments.', 'Overdue', (datetime.now() - timedelta(days=5)).isoformat(), (datetime.now() - timedelta(days=2)).isoformat(), 2)
        ]
        cursor.executemany("""
            INSERT INTO Tasks (title, description, status, created_date, due_date, contact_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, tasks)
        logging.info("Inserted 2 sample tasks.")

        # --- Link Contacts to Properties (Ownership) ---
        contact_properties = [
            (3, 3, 'Owner') # John Smith owns The Palm Tower unit
        ]
        cursor.executemany("""
            INSERT INTO ContactProperties (contact_id, property_id, relationship_type)
            VALUES (?, ?, ?)
        """, contact_properties)
        logging.info("Linked 1 contact to a property as owner.")

        conn.commit()
        logging.info("Sample data insertion was successful.")

    except sqlite3.Error as e:
        logging.error(f"An error occurred during sample data insertion: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    logging.info("Starting pre-deployment data setup...")
    clear_existing_data()
    insert_sample_data()
    logging.info("Script finished.")
