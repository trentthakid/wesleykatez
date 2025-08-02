import sqlite3
import database

def find_properties_in_text(text):
    """
    Scans a block of text for property names that exist in the database
    and returns a list of found properties.
    """
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT property_id, building, unit FROM Properties")
    all_properties = cursor.fetchall()
    conn.close()

    found_properties = []
    for prop_id, building, unit in all_properties:
        if building.lower() in text.lower() and unit.lower() in text.lower():
            found_properties.append({
                "property_id": prop_id,
                "building": building,
                "unit": unit
            })
    
    return found_properties

def process_text_for_entities(text):
    """
    A tool that takes a string of text, finds known entities like properties,
    and returns a structured response.
    """
    properties = find_properties_in_text(text)
    
    if not properties:
        return {"message": "I analyzed the text but did not find any properties from your database mentioned."}

    response_message = f"I analyzed the text and found mentions of {len(properties)} properties from your database:\n"
    for prop in properties:
        response_message += f"- {prop['unit']} in {prop['building']}\n"
    
    return {
        "message": response_message,
        "data": {
            "found_properties": properties
        }
    }
