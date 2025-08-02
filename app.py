import os
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3

# Import our custom modules
from database import init_database, get_db_connection
from automation import get_follow_up_tasks, find_matching_buyers, draft_follow_up_email, get_overdue_tasks, generate_daily_summary
from analytics import score_leads, get_lead_scores_tool, get_market_insights, get_performance_metrics, predict_deal_probability
from knowledge_base import find_properties_in_text, add_to_knowledge_base, search_knowledge_base, get_knowledge_statistics, get_relevant_context
from gemini_integration import GeminiClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_database()

# Initialize Gemini client
gemini_client = GeminiClient()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route handlers
@app.route('/')
def index():
    """Serve the main application page"""
    with open('static/index.html', 'r') as f:
        return f.read()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with AURA AI assistant"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Route the command through our two-tier system
        response = route_command(message)
        
        return jsonify({'message': response})
        
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

def route_command(user_input):
    """Two-tier cognitive engine: Tool-based routing + LLM escalation"""
    user_input_lower = user_input.lower()
    
    # Tier 1: Tool-based routing for specific commands
    if 'who owns' in user_input_lower or 'owner of' in user_input_lower:
        return find_owner(user_input)
    elif 'create task' in user_input_lower or 'add task' in user_input_lower:
        return create_task(user_input)
    elif 'follow up' in user_input_lower or 'follow-up' in user_input_lower:
        return get_follow_ups()
    elif 'lead score' in user_input_lower or 'score leads' in user_input_lower:
        return get_lead_scores_tool()
    elif 'find buyers' in user_input_lower or 'matching buyers' in user_input_lower:
        return find_buyers_for_property(user_input)
    elif 'property' in user_input_lower and ('find' in user_input_lower or 'search' in user_input_lower):
        return search_properties(user_input)
    elif 'market' in user_input_lower and ('insight' in user_input_lower or 'analysis' in user_input_lower):
        return get_market_analysis(user_input)
    elif 'performance' in user_input_lower or 'metrics' in user_input_lower:
        return get_performance_summary()
    elif 'daily briefing' in user_input_lower or 'briefing' in user_input_lower:
        return get_daily_briefing_summary()
    
    # Tier 2: LLM escalation for complex queries
    return llm_tool(user_input)

def find_owner(query):
    """Find the owner of a specific property"""
    try:
        # Extract property information from query
        properties = find_properties_in_text(query)
        
        if not properties:
            return "I couldn't identify a specific property in your query. Please provide the building name and unit number."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        results = []
        for prop in properties:
            cursor.execute("""
                SELECT c.name, c.email, c.phone, cp.relationship_type, p.building, p.unit
                FROM ContactProperties cp
                JOIN Contacts c ON cp.contact_id = c.id
                JOIN Properties p ON cp.property_id = p.id
                WHERE p.building LIKE ? AND p.unit LIKE ? AND cp.relationship_type = 'Owner'
            """, (f"%{prop['building']}%", f"%{prop['unit']}%"))
            
            owner_data = cursor.fetchone()
            if owner_data:
                results.append(f"Owner of {owner_data[4]} Unit {owner_data[5]}: {owner_data[0]} ({owner_data[1]}, {owner_data[2]})")
            else:
                results.append(f"No owner found for {prop['building']} Unit {prop['unit']}")
        
        conn.close()
        return "\n".join(results) if results else "No ownership information found."
        
    except Exception as e:
        logging.error(f"Error finding owner: {str(e)}")
        return "Sorry, I encountered an error while searching for ownership information."

def create_task(query):
    """Create a task from natural language input"""
    try:
        # Extract task details using basic parsing
        task_description = query.replace('create task', '').replace('add task', '').strip()
        
        if not task_description:
            return "Please provide a task description."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Tasks (title, description, status, created_date, due_date)
            VALUES (?, ?, 'Pending', ?, ?)
        """, (
            task_description[:100],  # Use first 100 chars as title
            task_description,
            datetime.now().isoformat(),
            (datetime.now() + timedelta(days=7)).isoformat()  # Default due date 7 days from now
        ))
        
        conn.commit()
        conn.close()
        
        return f"Task created successfully: '{task_description[:100]}'"
        
    except Exception as e:
        logging.error(f"Error creating task: {str(e)}")
        return "Sorry, I couldn't create the task. Please try again."

def get_follow_ups():
    """Get follow-up tasks"""
    try:
        follow_ups = get_follow_up_tasks()
        
        if not follow_ups:
            return "You're all caught up! No follow-ups needed at this time."
        
        response = "Here are your follow-up tasks:\n\n"
        for task in follow_ups[:5]:  # Limit to 5 most urgent
            response += f"• {task['name']} ({task['status']} lead) - {task['days_overdue']} days overdue\n"
        
        return response
        
    except Exception as e:
        logging.error(f"Error getting follow-ups: {str(e)}")
        return "Sorry, I couldn't retrieve your follow-up tasks."

def find_buyers_for_property(query):
    """Find potential buyers for a property"""
    try:
        # Extract property information
        properties = find_properties_in_text(query)
        
        if not properties:
            return "Please specify a property to find buyers for."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the first property mentioned
        prop = properties[0]
        cursor.execute("SELECT id FROM Properties WHERE building LIKE ? AND unit LIKE ?", 
                      (f"%{prop['building']}%", f"%{prop['unit']}%"))
        
        property_result = cursor.fetchone()
        if not property_result:
            return f"Property {prop['building']} Unit {prop['unit']} not found in database."
        
        buyers = find_matching_buyers(property_result[0])
        conn.close()
        
        if not buyers:
            return "No potential buyers found for this property."
        
        response = f"Potential buyers for {prop['building']} Unit {prop['unit']}:\n\n"
        for buyer in buyers[:3]:  # Limit to top 3
            response += f"• {buyer['name']} ({buyer['status']} lead) - {buyer['email']}\n"
        
        return response
        
    except Exception as e:
        logging.error(f"Error finding buyers: {str(e)}")
        return "Sorry, I couldn't find potential buyers."

def search_properties(query):
    """Search for properties based on query"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simple search in building and area fields
        search_term = query.replace('find property', '').replace('search property', '').strip()
        
        cursor.execute("""
            SELECT building, unit, area, property_type, bedrooms, bathrooms, price
            FROM Properties 
            WHERE building LIKE ? OR area LIKE ? OR property_type LIKE ?
            LIMIT 5
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        properties = cursor.fetchall()
        conn.close()
        
        if not properties:
            return f"No properties found matching '{search_term}'"
        
        response = f"Properties matching '{search_term}':\n\n"
        for prop in properties:
            response += f"• {prop[0]} Unit {prop[1]} - {prop[2]} ({prop[3]}) - {prop[4]}BR/{prop[5]}BA - AED {prop[6]:,.0f}\n"
        
        return response
        
    except Exception as e:
        logging.error(f"Error searching properties: {str(e)}")
        return "Sorry, I couldn't search for properties."

def get_market_analysis(query):
    """Get market analysis and insights"""
    try:
        # Extract area if mentioned
        area = None
        for word in query.split():
            if word.lower() in ['downtown', 'marina', 'palm', 'jumeirah', 'deira', 'bur', 'dubai']:
                area = word
                break
        
        insights = get_market_insights(area)
        
        if 'error' in insights:
            return "Sorry, I couldn't retrieve market insights at this time."
        
        response = f"Market Analysis for {insights['area']}:\n\n"
        response += f"Total Properties: {insights['summary']['total_properties']}\n"
        response += f"Average Price: AED {insights['summary']['average_market_price']:,.0f}\n"
        response += f"Most Common Type: {insights['summary']['most_common_type']}\n\n"
        
        if insights['property_types']:
            response += "By Property Type:\n"
            for prop_type in insights['property_types'][:3]:
                response += f"• {prop_type['type']}: {prop_type['count']} properties, Avg: AED {prop_type['average_price']:,.0f}\n"
        
        return response
        
    except Exception as e:
        logging.error(f"Error getting market analysis: {str(e)}")
        return "Sorry, I couldn't retrieve market analysis."

def get_performance_summary():
    """Get performance metrics summary"""
    try:
        metrics = get_performance_metrics()
        
        if 'error' in metrics:
            return "Sorry, I couldn't retrieve performance metrics at this time."
        
        response = "Performance Summary:\n\n"
        response += f"• Active Deals: {metrics.get('active_deals', 0)}\n"
        response += f"• Deals Closed (30 days): {metrics.get('deals_closed_30_days', 0)}\n"
        response += f"• Revenue (30 days): AED {metrics.get('revenue_30_days', 0):,.0f}\n"
        response += f"• Commission (30 days): AED {metrics.get('commission_30_days', 0):,.0f}\n"
        response += f"• Pipeline Value: AED {metrics.get('pipeline_value', 0):,.0f}\n"
        response += f"• Conversion Rate: {metrics.get('conversion_rate', 0)}%\n"
        response += f"• Average Deal Size: AED {metrics.get('average_deal_size', 0):,.0f}\n"
        response += f"• Task Completion Rate: {metrics.get('task_completion_rate', 0)}%\n"
        
        return response
        
    except Exception as e:
        logging.error(f"Error getting performance summary: {str(e)}")
        return "Sorry, I couldn't retrieve performance metrics."

def get_daily_briefing_summary():
    """Get daily briefing summary"""
    try:
        summary = generate_daily_summary()
        
        if 'error' in summary:
            return "Sorry, I couldn't generate your daily briefing."
        
        response = f"Daily Briefing for {summary['date']}:\n\n"
        response += summary['summary_message'] + "\n\n"
        
        if summary['urgent_follow_ups']:
            response += "Urgent Follow-ups:\n"
            for follow_up in summary['urgent_follow_ups']:
                response += f"• {follow_up['name']} ({follow_up['status']} lead) - {follow_up['days_overdue']} days overdue\n"
            response += "\n"
        
        if summary['urgent_overdue_tasks']:
            response += "Overdue Tasks:\n"
            for task in summary['urgent_overdue_tasks']:
                response += f"• {task['title']} - {task['days_overdue']} days overdue\n"
            response += "\n"
        
        if summary['todays_viewings']:
            response += "Today's Viewings:\n"
            for viewing in summary['todays_viewings']:
                response += f"• {viewing['contact_name']} - {viewing['property']}\n"
        
        return response
        
    except Exception as e:
        logging.error(f"Error getting daily briefing: {str(e)}")
        return "Sorry, I couldn't generate your daily briefing."

def llm_tool(query):
    """Handle complex queries using Gemini LLM"""
    try:
        # Get relevant context from database
        context = get_database_context()
        
        # Get relevant context from knowledge base
        knowledge_context = get_relevant_context(query)
        
        # Create a comprehensive prompt
        prompt = f"""
You are AURA, an AI assistant for a Dubai real estate professional. You have access to the following data context:

DATABASE CONTEXT:
{context}

KNOWLEDGE BASE CONTEXT:
{knowledge_context}

User Query: {query}

Please provide a helpful, accurate, and professional response. Use the context provided to give specific, actionable advice. If you need specific data that isn't in the context, suggest what the user should provide or how they can get that information.

Keep responses concise but comprehensive, and always maintain a professional tone suitable for a real estate expert.
"""
        
        response = gemini_client.generate_response(prompt)
        return response
        
    except Exception as e:
        logging.error(f"LLM tool error: {str(e)}")
        return "I'm having trouble processing that request right now. Please try rephrasing your question or contact support if the issue persists."

def get_database_context():
    """Get relevant context from database for LLM"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get summary statistics
        cursor.execute("SELECT COUNT(*) FROM Properties")
        property_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Contacts")
        contact_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Deals WHERE status = 'Active'")
        active_deals = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Tasks WHERE status = 'Pending'")
        pending_tasks = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute("""
            SELECT building, unit, area, price FROM Properties 
            ORDER BY id DESC LIMIT 5
        """)
        recent_properties = cursor.fetchall()
        
        conn.close()
        
        context = f"""
Database Summary:
- Total Properties: {property_count}
- Total Contacts: {contact_count}
- Active Deals: {active_deals}
- Pending Tasks: {pending_tasks}

Recent Properties:
"""
        for prop in recent_properties:
            context += f"- {prop[0]} Unit {prop[1]} in {prop[2]} - AED {prop[3]:,.0f}\n"
        
        return context
        
    except Exception as e:
        logging.error(f"Error getting database context: {str(e)}")
        return "Database context unavailable."

@app.route('/api/daily-briefing', methods=['GET'])
def daily_briefing():
    """Get daily briefing information"""
    try:
        follow_ups = get_follow_up_tasks()
        
        return jsonify({
            'success': True,
            'follow_ups': follow_ups[:5]  # Limit to 5 most urgent
        })
        
    except Exception as e:
        logging.error(f"Daily briefing error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate daily briefing'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process the file and add to knowledge base
                try:
                    add_to_knowledge_base(filepath, filename)
                    uploaded_files.append(filename)
                except Exception as e:
                    logging.error(f"Error processing file {filename}: {str(e)}")
        
        if uploaded_files:
            return jsonify({
                'message': f'Successfully uploaded and processed {len(uploaded_files)} files: {", ".join(uploaded_files)}'
            })
        else:
            return jsonify({'error': 'No valid files were uploaded'}), 400
            
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/analytics/leads', methods=['GET'])
def get_lead_analytics():
    """Get lead scoring analytics"""
    try:
        scores = score_leads()
        return jsonify({'success': True, 'lead_scores': scores})
    except Exception as e:
        logging.error(f"Lead analytics error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get lead analytics'}), 500

@app.route('/api/analytics/performance', methods=['GET'])
def get_performance_analytics():
    """Get performance metrics"""
    try:
        metrics = get_performance_metrics()
        return jsonify(metrics)
    except Exception as e:
        logging.error(f"Performance analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get performance metrics'}), 500

@app.route('/api/analytics/market', methods=['GET'])
def get_market_analytics():
    """Get market insights"""
    try:
        area = request.args.get('area')
        insights = get_market_insights(area)
        return jsonify(insights)
    except Exception as e:
        logging.error(f"Market analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get market insights'}), 500

@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all properties"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, building, unit, area, property_type, bedrooms, bathrooms, 
                   size_sqft, price, status, created_date
            FROM Properties
            ORDER BY created_date DESC
        """)
        
        properties = []
        for row in cursor.fetchall():
            properties.append({
                'id': row[0],
                'building': row[1],
                'unit': row[2],
                'area': row[3],
                'property_type': row[4],
                'bedrooms': row[5],
                'bathrooms': row[6],
                'size_sqft': row[7],
                'price': row[8],
                'status': row[9],
                'created_date': row[10]
            })
        
        conn.close()
        return jsonify({'success': True, 'properties': properties})
        
    except Exception as e:
        logging.error(f"Properties API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch properties'}), 500

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, phone, lead_status, last_contacted_date, created_date
            FROM Contacts
            ORDER BY created_date DESC
        """)
        
        contacts = []
        for row in cursor.fetchall():
            contacts.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'lead_status': row[4],
                'last_contacted_date': row[5],
                'created_date': row[6]
            })
        
        conn.close()
        return jsonify({'success': True, 'contacts': contacts})
        
    except Exception as e:
        logging.error(f"Contacts API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch contacts'}), 500

@app.route('/api/knowledge/stats', methods=['GET'])
def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = get_knowledge_statistics()
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Knowledge stats error: {str(e)}")
        return jsonify({'error': 'Failed to get knowledge statistics'}), 500

@app.route('/api/knowledge/search', methods=['GET'])
def search_knowledge():
    """Search knowledge base"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        results = search_knowledge_base(query, limit)
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logging.error(f"Knowledge search error: {str(e)}")
        return jsonify({'success': False, 'error': 'Search failed'}), 500

@app.route('/api/deals/predict', methods=['POST'])
def predict_deal():
    """Predict deal probability"""
    try:
        data = request.get_json()
        deal_id = data.get('deal_id')
        
        if not deal_id:
            return jsonify({'error': 'Deal ID is required'}), 400
        
        prediction = predict_deal_probability(deal_id)
        return jsonify(prediction)
        
    except Exception as e:
        logging.error(f"Deal prediction error: {str(e)}")
        return jsonify({'error': 'Failed to predict deal probability'}), 500

@app.route('/api/automation/email', methods=['POST'])
def draft_email():
    """Draft follow-up email"""
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')
        template_type = data.get('template_type', 'follow_up_hot')
        
        if not contact_id:
            return jsonify({'error': 'Contact ID is required'}), 400
        
        email_draft = draft_follow_up_email(contact_id, template_type)
        
        if email_draft:
            return jsonify({'success': True, 'email': email_draft})
        else:
            return jsonify({'success': False, 'error': 'Failed to draft email'})
        
    except Exception as e:
        logging.error(f"Email draft error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to draft email'}), 500

@app.route('/api/tasks/overdue', methods=['GET'])
def get_overdue_tasks_api():
    """Get overdue tasks"""
    try:
        overdue_tasks = get_overdue_tasks()
        return jsonify({'success': True, 'tasks': overdue_tasks})
    except Exception as e:
        logging.error(f"Overdue tasks error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get overdue tasks'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
