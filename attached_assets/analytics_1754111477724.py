import sqlite3
import database

def score_leads():
    """
    Analyzes contacts in the database and assigns a lead score.
    This is a simple rule-based scoring model for demonstration.
    - Hot = 100
    - Warm = 60
    - Cold = 20
    """
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, status FROM Contacts")
    contacts = cursor.fetchall()
    conn.close()

    scored_leads = []
    for name, status in contacts:
        score = 0
        if status == 'Hot':
            score = 100
        elif status == 'Warm':
            score = 60
        elif status == 'Cold':
            score = 20
        scored_leads.append({"name": name, "status": status, "score": score})
    
    # Sort by score descending
    scored_leads.sort(key=lambda x: x['score'], reverse=True)
    
    return scored_leads

def get_lead_scores_tool(entities):
    """
    A tool that scores all leads and returns a summary.
    """
    scored_leads = score_leads()

    if not scored_leads:
        return {"message": "There are no contacts in your database to score."}

    response_message = "Here are your contacts, scored and prioritized:\n"
    for lead in scored_leads:
        response_message += f"- {lead['name']} (Score: {lead['score']}, Status: {lead['status']})\n"
        
    return {
        "message": response_message,
        "data": {
            "scored_leads": scored_leads
        }
    }
