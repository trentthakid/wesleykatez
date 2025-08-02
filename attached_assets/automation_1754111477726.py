import sqlite3
import database

def find_matching_buyers(property_description):
    """
    Scans the database for contacts (buyers) who might be interested
    in a property matching the given description.

    For this initial version, it will find all contacts with a 'Warm' or 'Hot' status.
    Future versions could match based on saved search criteria for each contact.
    """
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    
    # Simple logic for now: find all active buyers.
    cursor.execute("SELECT name, email, phone FROM Contacts WHERE status IN ('Hot', 'Warm')")
    potential_buyers = cursor.fetchall()
    conn.close()

    if not potential_buyers:
        return {"message": "I didn't find any active buyers in your database that seem like a good match right now."}

    response_message = f"Based on your request for a '{property_description}', I found {len(potential_buyers)} potential buyers in your database:\n"
    buyer_list = []
    for name, email, phone in potential_buyers:
        response_message += f"- {name} ({email})\n"
        buyer_list.append({"name": name, "email": email, "phone": phone})

    response_message += "\nWould you like me to draft an outreach email for them?"
    
    return {
        "message": response_message,
        "data": {
            "potential_buyers": buyer_list
        }
    }

def get_follow_up_tasks():
    """
    Scans the database for contacts that need follow-ups and suggests tasks.
    - Hot leads: every 3 days
    - Warm leads: every 14 days
    - Cold leads: every 90 days
    """
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, status, last_contacted_date FROM Contacts")
    contacts = cursor.fetchall()
    conn.close()

    from datetime import datetime, timedelta

    today = datetime.now()
    follow_up_list = []

    for name, status, last_contact_str in contacts:
        if not last_contact_str:
            continue
        
        last_contact_date = datetime.strptime(last_contact_str, "%Y-%m-%d")
        days_since_contact = (today - last_contact_date).days

        due = False
        if status == 'Hot' and days_since_contact > 3:
            due = True
        elif status == 'Warm' and days_since_contact > 14:
            due = True
        elif status == 'Cold' and days_since_contact > 90:
            due = True
        
        if due:
            follow_up_list.append({
                "name": name,
                "status": status,
                "days_overdue": days_since_contact
            })
            
    return follow_up_list

def suggest_follow_ups_tool(entities):
    """Tool to get a list of suggested follow-up tasks."""
    tasks = get_follow_up_tasks()
    if not tasks:
        return {"message": "Great job! You are all caught up on your follow-ups."}

    response_message = "Based on your follow-up schedule, here are your suggested tasks:\n"
    for task in tasks:
        response_message += f"- Follow up with {task['name']} ({task['status']}). Last contact was {task['days_overdue']} days ago.\n"

    return {"message": response_message, "data": {"follow_up_tasks": tasks}}

def draft_follow_up_email(contact_name, template_name="General Follow-Up"):
    """
    Finds a contact and drafts a follow-up email using a template from the database.
    """
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    
    # Fetch contact
    cursor.execute("SELECT name, email, phone FROM Contacts WHERE name LIKE ?", (f'%{contact_name}%',))
    contact = cursor.fetchone()
    if not contact:
        conn.close()
        return {"error": f"I could not find a contact named '{contact_name}'."}
    name, email, phone = contact

    # Fetch template
    cursor.execute("SELECT subject, body FROM EmailTemplates WHERE name = ?", (template_name,))
    template = cursor.fetchone()
    if not template:
        conn.close()
        return {"error": f"Email template '{template_name}' not found."}
    subject_template, body_template = template
    
    conn.close()

    # Personalize the template
    subject = subject_template.format(contact_name=name)
    body = body_template.format(contact_name=name)

    return {
        "message": f"Here is a draft email to {name} using the '{template_name}' template.",
        "ui_component": "email_drafter",
        "data": {
            "recipient_name": name,
            "recipient_email": email,
            "recipient_phone": phone,
            "subject": subject,
            "body": body
        }
    }
