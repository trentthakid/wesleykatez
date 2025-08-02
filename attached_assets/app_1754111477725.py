from flask import Flask, jsonify, request, send_from_directory
import database
import sqlite3
import os
from weasyprint import HTML
from datetime import datetime
import knowledge_base
import automation
import analytics
import google.generativeai as genai
import json

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyDTxtS_0wEtBw3eD51PgAiQ2gPjbhtr4RQ"
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__, static_folder='static')

# --- Database Initialization ---
database.init_db()

# --- AURA 2.0: Tool-Based Cognitive Engine (Functions from before) ---
def find_owner(entities):
    """Tool to find the owner of a property."""
    building = entities.get("building")
    unit = entities.get("unit")
    if not building or not unit:
        return {"error": "Please specify a building and unit number."}

    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, c.phone, c.email FROM ContactProperties cp
        JOIN Contacts c ON cp.contact_id = c.contact_id
        JOIN Properties p ON cp.property_id = p.property_id
        WHERE LOWER(p.building) = ? AND p.unit = ? AND cp.role = 'Owner'
    """, (building.lower(), unit))
    owner = cursor.fetchone()
    conn.close()

    if owner:
        return {
            "message": f"The owner of {unit} in {building} is {owner[0]}. Contact: {owner[1]}, {owner[2]}.",
            "data": {"owner_name": owner[0], "phone": owner[1], "email": owner[2]}
        }
    else:
        return {
            "message": f"I could not find an owner for {unit} in {building} in your records.",
            "recommended_action": {
                "action": "create_task",
                "details": {"task": f"Research owner of {unit} {building}"}
            }
        }

def create_task(entities):
    """Tool to create a new task."""
    description = entities.get("task_description")
    if not description:
        return {"error": "What is the task you'd like to create?"}
    
    try:
        conn = sqlite3.connect(database.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Tasks (description, due_date, status) VALUES (?, ?, 'Pending')",
                       (description, entities.get('date', 'N/A')))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return {"message": f"Task #{task_id} '{description}' has been created."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

def llm_tool(message):
    """Tier 2: Escalates complex queries to the LLM for interpretation."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are AURA, a real estate AI assistant. Your task is to interpret the user's request and respond in a conversational, human-like manner.
    User's request: "{message}"
    
    Based on this, provide a helpful, direct response. If you can infer a specific action, suggest it.
    """
    try:
        response = model.generate_content(prompt)
        return {"message": response.text}
    except Exception as e:
        return {"error": f"Gemini API error: {str(e)}"}

TOOLS = {
    "find_owner": {"keywords": ["who owns", "owner of"], "function": find_owner},
    "create_task": {"keywords": ["create task", "remind me to"], "function": create_task},
}

def route_command(message):
    """Routes command to a tool or escalates to the LLM."""
    message_lower = message.lower()
    for tool_name, config in TOOLS.items():
        for keyword in config["keywords"]:
            if keyword in message_lower:
                entities = {}
                if tool_name == "find_owner":
                    parts = message_lower.split(" in ")
                    if len(parts) > 1:
                        entities["building"] = parts[1].strip()
                        entities["unit"] = next((word for word in parts[0].split() if word.isdigit()), None)
                elif tool_name == "create_task":
                    entities["task_description"] = message.replace(keyword, "").strip()
                return config["function"](entities)
    
    return llm_tool(message)

# --- Main API Endpoints ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"success": False, "error": "Empty message"})

    result = route_command(user_message)
    
    response = {
        "success": "error" not in result,
        "message": result.get("message"),
        "error": result.get("error"),
        "ui_component": result.get("ui_component"),
        "data": result.get("data"),
        "recommended_action": result.get("recommended_action")
    }
    return jsonify(response)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"success": False, "error": "No files part in the request"})
    
    files = request.files.getlist('files')
    saved_files = []
    for file in files:
        if file.filename == '':
            continue
        if file:
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            saved_files.append(filename)
            
    return jsonify({"success": True, "message": f"{len(saved_files)} files uploaded successfully."})

@app.route('/api/daily-briefing')
def daily_briefing():
    """Get the daily briefing tasks."""
    try:
        follow_ups = automation.get_follow_up_tasks()
        return jsonify({"success": True, "follow_ups": follow_ups})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
