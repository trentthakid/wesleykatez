import sqlite3
import os

DB_PATH = "data/aura.db"

def insert_data():
    """Inserts sample data into the database."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Please run database.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Clear existing data to avoid duplicates
        cursor.execute("DELETE FROM ContactProperties")
        cursor.execute("DELETE FROM HistoricalTransactions")
        cursor.execute("DELETE FROM Properties")
        cursor.execute("DELETE FROM Contacts")
        cursor.execute("DELETE FROM Tasks")
        print("Cleared existing data.")

        # --- Insert Sample Properties ---
        properties = [
            ("Oceana Adriatic", "303", 3, "Sea View", 1200, 2, "2BR"),
            ("Marina Residences 4", "505", 5, "Marina View", 1500, 3, "3BR"),
            ("Shoreline Apartments", "Al Das 101", 1, "Park View", 800, 1, "1BR"),
            ("Seven Palm", "North 707", 7, "Burj Al Arab View", 950, 1, "1BR"),
        ]
        cursor.executemany("INSERT INTO Properties (building, unit, floor, view, size_sqft, bedrooms, layout_type) VALUES (?, ?, ?, ?, ?, ?, ?)", properties)
        print(f"Inserted {len(properties)} properties.")

        # --- Get Property IDs for linking ---
        cursor.execute("SELECT property_id, building, unit FROM Properties")
        property_map = {f"{p[1]}-{p[2]}": p[0] for p in cursor.fetchall()}

        # --- Insert Sample Contacts ---
        contacts = [
            ("Ahmed Al Mansouri", "+971501112222", "ahmed.m@example.com", "Hot", "2025-07-28"),
            ("Sarah Johnson", "+971553334444", "sarah.j@example.com", "Warm", "2025-07-15"),
            ("John Smith", "+971525556666", "john.s@example.com", "Cold", "2025-06-01"),
        ]
        cursor.executemany("INSERT INTO Contacts (name, phone, email, status, last_contacted_date) VALUES (?, ?, ?, ?, ?)", contacts)
        print(f"Inserted {len(contacts)} contacts.")

        # --- Get Contact IDs for linking ---
        cursor.execute("SELECT contact_id, name FROM Contacts")
        contact_map = {c[1]: c[0] for c in cursor.fetchall()}

        # --- Link Contacts to Properties (as Owners) ---
        links = [
            (contact_map["Ahmed Al Mansouri"], property_map["Marina Residences 4-505"], "Owner"),
            (contact_map["Sarah Johnson"], property_map["Oceana Adriatic-303"], "Owner"),
        ]
        cursor.executemany("INSERT INTO ContactProperties (contact_id, property_id, role) VALUES (?, ?, ?)", links)
        print(f"Linked {len(links)} owners to properties.")

        # --- Insert Historical Transactions ---
        transactions = [
            (property_map["Marina Residences 4-505"], 2800000, "2024-11-15"),
            (property_map["Oceana Adriatic-303"], 2100000, "2024-10-05"),
            (property_map["Shoreline Apartments-Al Das 101"], 1500000, "2024-09-20"),
        ]
        cursor.executemany("INSERT INTO HistoricalTransactions (property_id, sale_price_aed, sale_date) VALUES (?, ?, ?)", transactions)
        print(f"Inserted {len(transactions)} historical transactions.")

        # --- Insert Email Templates ---
        templates = [
            ("General Follow-Up", "Checking in, {contact_name}", "Hi {contact_name},\n\nJust wanted to touch base and see if there is anything I can help with regarding your property search.\n\nBest regards,\n[Your Name]"),
            ("New Listing Notification", "New Property Alert: {property_address}", "Hi {contact_name},\n\nA new property just came on the market that I think you might be interested in: {property_address}.\n\nLet me know if you'd like to schedule a viewing.\n\nBest regards,\n[Your Name]")
        ]
        cursor.executemany("INSERT INTO EmailTemplates (name, subject, body) VALUES (?, ?, ?)", templates)
        print(f"Inserted {len(templates)} email templates.")

        conn.commit()
        print("Sample data inserted successfully!")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    insert_data()
