"""
Automation module for the Digital Twin real estate application.
Provides intelligent tools to reduce manual effort and automate routine tasks.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database import get_db_connection

def get_follow_up_tasks() -> List[Dict[str, Any]]:
    """
    Get contacts that need follow-up based on lead status and last contact date.
    Returns a prioritized list of follow-up tasks.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Define follow-up intervals by lead status
        follow_up_intervals = {
            'Hot': 1,    # 1 day
            'Warm': 3,   # 3 days
            'Cold': 7    # 7 days
        }
        
        follow_ups = []
        current_date = datetime.now()
        
        for status, interval in follow_up_intervals.items():
            cutoff_date = (current_date - timedelta(days=interval)).isoformat()
            
            cursor.execute("""
                SELECT id, name, email, phone, lead_status, last_contacted_date, created_date
                FROM Contacts 
                WHERE lead_status = ? 
                AND (last_contacted_date IS NULL OR last_contacted_date < ?)
                ORDER BY 
                    CASE 
                        WHEN last_contacted_date IS NULL THEN created_date
                        ELSE last_contacted_date
                    END ASC
            """, (status, cutoff_date))
            
            contacts = cursor.fetchall()
            
            for contact in contacts:
                last_contact_str = contact[5] or contact[6]  # Use created_date if last_contacted is null
                if last_contact_str:
                    try:
                        last_contact_date = datetime.fromisoformat(last_contact_str.replace('Z', '+00:00').split('+')[0])
                        days_overdue = (current_date - last_contact_date).days
                    except (ValueError, AttributeError):
                        days_overdue = interval + 1  # Default to overdue if can't parse date
                else:
                    days_overdue = interval + 1
                
                if days_overdue >= interval:
                    follow_ups.append({
                        'contact_id': contact[0],
                        'name': contact[1],
                        'email': contact[2],
                        'phone': contact[3],
                        'status': contact[4],
                        'last_contacted_date': contact[5],
                        'days_overdue': days_overdue,
                        'priority': _calculate_follow_up_priority(status, days_overdue)
                    })
        
        conn.close()
        
        # Sort by priority (Hot leads first, then by days overdue)
        follow_ups.sort(key=lambda x: (-x['priority'], -x['days_overdue']))
        
        return follow_ups
        
    except Exception as e:
        logging.error(f"Error getting follow-up tasks: {str(e)}")
        return []

def _calculate_follow_up_priority(status: str, days_overdue: int) -> int:
    """Calculate priority score for follow-up tasks"""
    base_priority = {
        'Hot': 100,
        'Warm': 60,
        'Cold': 20
    }.get(status, 10)
    
    # Add urgency based on how overdue the follow-up is
    urgency_bonus = min(days_overdue * 10, 50)  # Cap at 50 bonus points
    
    return base_priority + urgency_bonus

def find_matching_buyers(property_id: int) -> List[Dict[str, Any]]:
    """
    Find potential buyers for a given property based on their profile and preferences.
    Currently matches based on lead status; can be extended for more sophisticated matching.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get property details first
        cursor.execute("""
            SELECT property_type, bedrooms, bathrooms, price, area
            FROM Properties WHERE id = ?
        """, (property_id,))
        
        property_data = cursor.fetchone()
        if not property_data:
            return []
        
        # Find potential buyers (Hot and Warm leads who are not already owners)
        cursor.execute("""
            SELECT DISTINCT c.id, c.name, c.email, c.phone, c.lead_status, c.notes
            FROM Contacts c
            WHERE c.lead_status IN ('Hot', 'Warm')
            AND c.id NOT IN (
                SELECT cp.contact_id FROM ContactProperties cp 
                WHERE cp.relationship_type = 'Owner'
            )
            ORDER BY 
                CASE c.lead_status 
                    WHEN 'Hot' THEN 1 
                    WHEN 'Warm' THEN 2 
                    ELSE 3 
                END,
                c.name
        """)
        
        potential_buyers = []
        for contact in cursor.fetchall():
            # Calculate match score based on various factors
            match_score = _calculate_buyer_match_score(
                contact, property_data
            )
            
            potential_buyers.append({
                'contact_id': contact[0],
                'name': contact[1],
                'email': contact[2],
                'phone': contact[3],
                'status': contact[4],
                'notes': contact[5] or '',
                'match_score': match_score
            })
        
        conn.close()
        
        # Sort by match score (highest first)
        potential_buyers.sort(key=lambda x: x['match_score'], reverse=True)
        
        return potential_buyers
        
    except Exception as e:
        logging.error(f"Error finding matching buyers: {str(e)}")
        return []

def _calculate_buyer_match_score(contact, property_data) -> float:
    """
    Calculate how well a contact matches a property.
    This is a simplified version - can be enhanced with ML models.
    """
    base_score = {
        'Hot': 100,
        'Warm': 70,
        'Cold': 30
    }.get(contact[4], 10)  # contact[4] is lead_status
    
    # Add points based on notes containing relevant keywords
    notes = (contact[5] or '').lower()
    property_type = property_data[0].lower() if property_data[0] else ''
    area = property_data[4].lower() if property_data[4] else ''
    
    if property_type in notes:
        base_score += 20
    if area in notes:
        base_score += 15
    if 'urgent' in notes or 'asap' in notes:
        base_score += 10
    
    return base_score

def draft_follow_up_email(contact_id: int, template_type: str = 'follow_up_hot') -> Optional[Dict[str, str]]:
    """
    Draft a personalized follow-up email for a contact using email templates.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get contact information
        cursor.execute("""
            SELECT name, email, lead_status, notes
            FROM Contacts WHERE id = ?
        """, (contact_id,))
        
        contact = cursor.fetchone()
        if not contact:
            return None
        
        # Get appropriate email template
        cursor.execute("""
            SELECT subject, body, variables
            FROM EmailTemplates 
            WHERE template_name = ? OR template_type = ?
            LIMIT 1
        """, (template_type, template_type))
        
        template = cursor.fetchone()
        if not template:
            # Use default template
            template = (
                "Follow-up",
                "Hi {name},\n\nI wanted to follow up with you regarding your real estate needs.\n\nBest regards,\nYour Real Estate Agent",
                "name"
            )
        
        # Get any recent property interests
        cursor.execute("""
            SELECT p.building, p.unit, p.area
            FROM Properties p
            JOIN ContactProperties cp ON p.id = cp.property_id
            WHERE cp.contact_id = ? AND cp.relationship_type = 'Interested'
            ORDER BY cp.created_date DESC
            LIMIT 1
        """, (contact_id,))
        
        property_interest = cursor.fetchone()
        property_info = f"{property_interest[0]} Unit {property_interest[1]} in {property_interest[2]}" if property_interest else "properties in your area"
        
        conn.close()
        
        # Personalize the email
        personalized_subject = template[0].format(
            name=contact[0],
            property=property_info
        )
        
        personalized_body = template[1].format(
            name=contact[0],
            property=property_info,
            status=contact[2]
        )
        
        return {
            'to_email': str(contact[1]),
            'to_name': str(contact[0]),
            'subject': str(personalized_subject),
            'body': str(personalized_body),
            'contact_id': str(contact_id)
        }
        
    except Exception as e:
        logging.error(f"Error drafting follow-up email: {str(e)}")
        return None

def schedule_property_viewing(contact_id: int, property_id: int, viewing_date: str) -> bool:
    """
    Schedule a property viewing and create associated tasks.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create a viewing task
        task_title = f"Property viewing scheduled"
        task_description = f"Viewing scheduled for contact ID {contact_id} at property ID {property_id} on {viewing_date}"
        
        cursor.execute("""
            INSERT INTO Tasks (title, description, status, priority, contact_id, property_id, 
                             created_date, due_date)
            VALUES (?, ?, 'Scheduled', 'High', ?, ?, ?, ?)
        """, (
            task_title,
            task_description,
            contact_id,
            property_id,
            datetime.now().isoformat(),
            viewing_date
        ))
        
        # Update contact-property relationship
        cursor.execute("""
            INSERT OR REPLACE INTO ContactProperties 
            (contact_id, property_id, relationship_type, created_date)
            VALUES (?, ?, 'Viewing Scheduled', ?)
        """, (contact_id, property_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Viewing scheduled successfully for contact {contact_id} and property {property_id}")
        return True
        
    except Exception as e:
        logging.error(f"Error scheduling viewing: {str(e)}")
        return False

def update_lead_last_contacted(contact_id: int) -> bool:
    """
    Update the last contacted date for a lead.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Contacts 
            SET last_contacted_date = ?, updated_date = ?
            WHERE id = ?
        """, (
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            contact_id
        ))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logging.error(f"Error updating last contacted date: {str(e)}")
        return False

def get_overdue_tasks() -> List[Dict[str, Any]]:
    """
    Get all overdue tasks.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_date = datetime.now().isoformat()
        
        cursor.execute("""
            SELECT t.id, t.title, t.description, t.priority, t.due_date,
                   c.name as contact_name, p.building, p.unit
            FROM Tasks t
            LEFT JOIN Contacts c ON t.contact_id = c.id
            LEFT JOIN Properties p ON t.property_id = p.id
            WHERE t.status != 'Completed' AND t.due_date < ?
            ORDER BY t.due_date ASC
        """, (current_date,))
        
        overdue_tasks = []
        for row in cursor.fetchall():
            try:
                due_date = datetime.fromisoformat(row[4].replace('Z', '+00:00').split('+')[0])
                days_overdue = (datetime.now() - due_date).days
            except (ValueError, AttributeError):
                days_overdue = 0
            
            overdue_tasks.append({
                'task_id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'due_date': row[4],
                'contact_name': row[5],
                'property': f"{row[6]} Unit {row[7]}" if row[6] and row[7] else None,
                'days_overdue': days_overdue
            })
        
        conn.close()
        return overdue_tasks
        
    except Exception as e:
        logging.error(f"Error getting overdue tasks: {str(e)}")
        return []

def generate_daily_summary() -> Dict[str, Any]:
    """
    Generate a comprehensive daily summary for the agent.
    """
    try:
        follow_ups = get_follow_up_tasks()
        overdue_tasks = get_overdue_tasks()
        
        # Get today's scheduled viewings
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT t.title, c.name, p.building, p.unit
            FROM Tasks t
            JOIN Contacts c ON t.contact_id = c.id
            LEFT JOIN Properties p ON t.property_id = p.id
            WHERE DATE(t.due_date) = ? AND t.title LIKE '%viewing%'
            ORDER BY t.due_date
        """, (today,))
        
        todays_viewings = [
            {
                'title': row[0],
                'contact_name': row[1],
                'property': f"{row[2]} Unit {row[3]}" if row[2] and row[3] else "Property TBD"
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'follow_ups_count': len(follow_ups),
            'urgent_follow_ups': [f for f in follow_ups if f['priority'] > 100][:3],
            'overdue_tasks_count': len(overdue_tasks),
            'urgent_overdue_tasks': overdue_tasks[:3],
            'todays_viewings': todays_viewings,
            'summary_message': _generate_summary_message(follow_ups, overdue_tasks, todays_viewings)
        }
        
    except Exception as e:
        logging.error(f"Error generating daily summary: {str(e)}")
        return {'error': 'Failed to generate daily summary'}

def _generate_summary_message(follow_ups, overdue_tasks, viewings) -> str:
    """Generate a human-readable summary message"""
    messages = []
    
    if follow_ups:
        urgent_count = len([f for f in follow_ups if f['priority'] > 100])
        if urgent_count > 0:
            messages.append(f"{urgent_count} urgent follow-ups needed")
        else:
            messages.append(f"{len(follow_ups)} follow-ups pending")
    
    if overdue_tasks:
        messages.append(f"{len(overdue_tasks)} overdue tasks")
    
    if viewings:
        messages.append(f"{len(viewings)} viewings scheduled today")
    
    if not messages:
        return "You're all caught up! Great job staying on top of your tasks."
    
    return "Today's priorities: " + ", ".join(messages) + "."
