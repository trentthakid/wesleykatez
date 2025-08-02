"""
Analytics module for the Digital Twin real estate application.
Provides tools for data analysis, lead scoring, and strategic insights.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from database import get_db_connection
import json

def score_leads() -> List[Dict[str, Any]]:
    """
    Score all leads based on multiple factors and return prioritized list.
    Implements a comprehensive lead scoring algorithm.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all contacts with their interaction history
        cursor.execute("""
            SELECT c.id, c.name, c.email, c.phone, c.lead_status, c.source, 
                   c.last_contacted_date, c.created_date, c.notes
            FROM Contacts c
            ORDER BY c.created_date DESC
        """)
        
        contacts = cursor.fetchall()
        scored_leads = []
        
        for contact in contacts:
            score_data = _calculate_lead_score(contact, cursor)
            
            scored_leads.append({
                'contact_id': contact[0],
                'name': contact[1],
                'email': contact[2],
                'phone': contact[3],
                'lead_status': contact[4],
                'source': contact[5],
                'score': score_data['total_score'],
                'score_breakdown': score_data['breakdown'],
                'priority_level': _get_priority_level(score_data['total_score']),
                'recommendation': score_data['recommendation']
            })
        
        # Update lead scores in database
        _update_lead_scores_in_db(scored_leads, cursor, conn)
        
        conn.close()
        
        # Sort by score (highest first)
        scored_leads.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_leads
        
    except Exception as e:
        logging.error(f"Error scoring leads: {str(e)}")
        return []

def _calculate_lead_score(contact, cursor) -> Dict[str, Any]:
    """
    Calculate comprehensive lead score based on multiple factors.
    """
    total_score = 0
    breakdown = {}
    
    # Factor 1: Lead Status (40% weight)
    status_scores = {'Hot': 100, 'Warm': 60, 'Cold': 20}
    status_score = status_scores.get(contact[4], 10)
    total_score += status_score * 0.4
    breakdown['lead_status'] = status_score
    
    # Factor 2: Lead Source (15% weight)
    source_scores = {
        'Referral': 90,
        'Previous Client': 85,
        'Social Media': 70,
        'Website': 60,
        'Walk-in': 50,
        'Cold Call': 30
    }
    source_score = source_scores.get(contact[5], 40)
    total_score += source_score * 0.15
    breakdown['source'] = source_score
    
    # Factor 3: Recency of Contact (20% weight)
    recency_score = _calculate_recency_score(contact[6], contact[7])
    total_score += recency_score * 0.2
    breakdown['recency'] = recency_score
    
    # Factor 4: Engagement Level (15% weight)
    engagement_score = _calculate_engagement_score(contact[0], cursor)
    total_score += engagement_score * 0.15
    breakdown['engagement'] = engagement_score
    
    # Factor 5: Intent Signals (10% weight)
    intent_score = _calculate_intent_score(contact[8])  # Notes field
    total_score += intent_score * 0.1
    breakdown['intent'] = intent_score
    
    # Generate recommendation based on score
    recommendation = _generate_lead_recommendation(total_score, breakdown, contact)
    
    return {
        'total_score': round(total_score, 1),
        'breakdown': breakdown,
        'recommendation': recommendation
    }

def _calculate_recency_score(last_contacted_date, created_date) -> float:
    """Calculate score based on how recently the lead was contacted."""
    try:
        # Use last contacted date if available, otherwise use created date
        reference_date_str = last_contacted_date or created_date
        if not reference_date_str:
            return 30  # Default score for unknown dates
        
        reference_date = datetime.fromisoformat(reference_date_str.replace('Z', '+00:00').split('+')[0])
        days_since = (datetime.now() - reference_date).days
        
        # Score decreases over time
        if days_since <= 1:
            return 100
        elif days_since <= 3:
            return 80
        elif days_since <= 7:
            return 60
        elif days_since <= 30:
            return 40
        elif days_since <= 90:
            return 20
        else:
            return 10
            
    except (ValueError, AttributeError):
        return 30  # Default score for invalid dates

def _calculate_engagement_score(contact_id, cursor) -> float:
    """Calculate engagement score based on interactions."""
    try:
        # Count property interests
        cursor.execute("""
            SELECT COUNT(*) FROM ContactProperties 
            WHERE contact_id = ? AND relationship_type IN ('Interested', 'Viewing Scheduled')
        """, (contact_id,))
        
        property_interests = cursor.fetchone()[0]
        
        # Count tasks related to this contact
        cursor.execute("""
            SELECT COUNT(*) FROM Tasks WHERE contact_id = ?
        """, (contact_id,))
        
        task_count = cursor.fetchone()[0]
        
        # Calculate score based on engagement indicators
        engagement_score = min(property_interests * 30 + task_count * 20, 100)
        
        return engagement_score
        
    except Exception:
        return 30  # Default score if calculation fails

def _calculate_intent_score(notes) -> float:
    """Calculate intent score based on notes content."""
    if not notes:
        return 30
    
    notes_lower = notes.lower()
    
    # High intent keywords
    high_intent_keywords = ['urgent', 'asap', 'ready to buy', 'cash buyer', 'pre-approved', 'mortgage approved']
    medium_intent_keywords = ['interested', 'looking for', 'budget', 'timeline', 'viewing']
    negative_keywords = ['not interested', 'postpone', 'delay', 'maybe later']
    
    score = 50  # Base score
    
    for keyword in high_intent_keywords:
        if keyword in notes_lower:
            score += 20
    
    for keyword in medium_intent_keywords:
        if keyword in notes_lower:
            score += 10
    
    for keyword in negative_keywords:
        if keyword in notes_lower:
            score -= 15
    
    return max(min(score, 100), 0)  # Keep score between 0-100

def _generate_lead_recommendation(total_score, breakdown, contact) -> str:
    """Generate actionable recommendation for the lead."""
    recommendations = []
    
    if total_score >= 80:
        recommendations.append("HIGH PRIORITY: Contact immediately")
    elif total_score >= 60:
        recommendations.append("MEDIUM PRIORITY: Follow up within 24 hours")
    else:
        recommendations.append("LOW PRIORITY: Include in weekly follow-up cycle")
    
    # Specific recommendations based on breakdown
    if breakdown['recency'] < 40:
        recommendations.append("Re-engagement needed - contact has gone cold")
    
    if breakdown['engagement'] < 30:
        recommendations.append("Increase engagement - send property suggestions")
    
    if breakdown['intent'] > 70:
        recommendations.append("High intent detected - prepare property options")
    
    return "; ".join(recommendations)

def _get_priority_level(score) -> str:
    """Get priority level based on score."""
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    elif score >= 40:
        return "Low"
    else:
        return "Very Low"

def _update_lead_scores_in_db(scored_leads, cursor, conn):
    """Update lead scores in the database."""
    try:
        current_time = datetime.now().isoformat()
        
        for lead in scored_leads:
            # Insert or update lead score
            cursor.execute("""
                INSERT OR REPLACE INTO LeadScores 
                (contact_id, score, score_factors, last_calculated)
                VALUES (?, ?, ?, ?)
            """, (
                lead['contact_id'],
                lead['score'],
                json.dumps(lead['score_breakdown']),
                current_time
            ))
        
        conn.commit()
        
    except Exception as e:
        logging.error(f"Error updating lead scores in database: {str(e)}")

def get_lead_scores_tool() -> str:
    """
    Tool function to get lead scores in a formatted string for AURA.
    """
    try:
        scores = score_leads()
        
        if not scores:
            return "No leads found to score."
        
        # Format top 5 leads
        response = "Lead Scoring Results (Top 5):\n\n"
        
        for i, lead in enumerate(scores[:5], 1):
            response += f"{i}. {lead['name']} - Score: {lead['score']:.1f} ({lead['priority_level']} Priority)\n"
            response += f"   Status: {lead['lead_status']} | Source: {lead['source']}\n"
            response += f"   Recommendation: {lead['recommendation']}\n\n"
        
        return response
        
    except Exception as e:
        logging.error(f"Error in get_lead_scores_tool: {str(e)}")
        return "Error calculating lead scores."

def get_market_insights(area: str = None) -> Dict[str, Any]:
    """
    Get market insights for a specific area or overall market.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query for market data
        if area:
            cursor.execute("""
                SELECT AVG(price), COUNT(*), MIN(price), MAX(price), 
                       AVG(size_sqft), property_type
                FROM Properties 
                WHERE area LIKE ? AND status = 'Available'
                GROUP BY property_type
            """, (f"%{area}%",))
        else:
            cursor.execute("""
                SELECT AVG(price), COUNT(*), MIN(price), MAX(price), 
                       AVG(size_sqft), property_type
                FROM Properties 
                WHERE status = 'Available'
                GROUP BY property_type
            """)
        
        market_data = cursor.fetchall()
        
        insights = {
            'area': area or 'Overall Market',
            'property_types': [],
            'summary': {}
        }
        
        total_properties = 0
        total_value = 0
        
        for row in market_data:
            avg_price, count, min_price, max_price, avg_size, prop_type = row
            
            total_properties += count
            total_value += avg_price * count if avg_price else 0
            
            insights['property_types'].append({
                'type': prop_type,
                'average_price': round(avg_price, 2) if avg_price else 0,
                'count': count,
                'price_range': {
                    'min': min_price,
                    'max': max_price
                },
                'average_size_sqft': round(avg_size, 2) if avg_size else 0,
                'price_per_sqft': round(avg_price / avg_size, 2) if avg_price and avg_size else 0
            })
        
        insights['summary'] = {
            'total_properties': total_properties,
            'average_market_price': round(total_value / total_properties, 2) if total_properties > 0 else 0,
            'most_common_type': max(insights['property_types'], key=lambda x: x['count'])['type'] if insights['property_types'] else 'N/A'
        }
        
        conn.close()
        return insights
        
    except Exception as e:
        logging.error(f"Error getting market insights: {str(e)}")
        return {'error': 'Failed to get market insights'}

def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics for the real estate business.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get date ranges
        today = datetime.now()
        thirty_days_ago = (today - timedelta(days=30)).isoformat()
        ninety_days_ago = (today - timedelta(days=90)).isoformat()
        
        metrics = {}
        
        # Active deals
        cursor.execute("SELECT COUNT(*) FROM Deals WHERE status = 'Active'")
        metrics['active_deals'] = cursor.fetchone()[0]
        
        # Closed deals last 30 days
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(deal_value), 0), COALESCE(SUM(commission), 0)
            FROM Deals 
            WHERE status = 'Closed' AND closing_date >= ?
        """, (thirty_days_ago,))
        
        closed_30_data = cursor.fetchone()
        metrics['deals_closed_30_days'] = closed_30_data[0]
        metrics['revenue_30_days'] = closed_30_data[1]
        metrics['commission_30_days'] = closed_30_data[2]
        
        # Pipeline value
        cursor.execute("SELECT COALESCE(SUM(deal_value), 0) FROM Deals WHERE status = 'Active'")
        metrics['pipeline_value'] = cursor.fetchone()[0]
        
        # Lead conversion rate (contacts to deals)
        cursor.execute("SELECT COUNT(*) FROM Contacts")
        total_contacts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT contact_id) FROM Deals")
        contacts_with_deals = cursor.fetchone()[0]
        
        metrics['conversion_rate'] = round((contacts_with_deals / total_contacts * 100), 2) if total_contacts > 0 else 0
        
        # Average deal size
        cursor.execute("SELECT AVG(deal_value) FROM Deals WHERE status = 'Closed' AND closing_date >= ?", (ninety_days_ago,))
        avg_deal_size = cursor.fetchone()[0]
        metrics['average_deal_size'] = round(avg_deal_size, 2) if avg_deal_size else 0
        
        # Task completion rate
        cursor.execute("SELECT COUNT(*) FROM Tasks WHERE status = 'Completed' AND completed_date >= ?", (thirty_days_ago,))
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Tasks WHERE created_date >= ?", (thirty_days_ago,))
        total_tasks = cursor.fetchone()[0]
        
        metrics['task_completion_rate'] = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
        
        conn.close()
        return metrics
        
    except Exception as e:
        logging.error(f"Error getting performance metrics: {str(e)}")
        return {'error': 'Failed to get performance metrics'}

def predict_deal_probability(deal_id: int) -> Dict[str, Any]:
    """
    Predict the probability of a deal closing based on historical data and current factors.
    This is a simplified version - can be enhanced with ML models.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get deal information
        cursor.execute("""
            SELECT d.id, d.deal_value, d.created_date, d.status,
                   c.lead_status, c.source, c.last_contacted_date,
                   p.property_type, p.price
            FROM Deals d
            JOIN Contacts c ON d.contact_id = c.id
            JOIN Properties p ON d.property_id = p.id
            WHERE d.id = ?
        """, (deal_id,))
        
        deal_data = cursor.fetchone()
        if not deal_data:
            return {'error': 'Deal not found'}
        
        # Calculate probability based on various factors
        probability_factors = {}
        total_probability = 50  # Base probability
        
        # Factor 1: Lead status
        lead_status_impact = {'Hot': 30, 'Warm': 15, 'Cold': -20}
        lead_impact = lead_status_impact.get(deal_data[4], 0)
        total_probability += lead_impact
        probability_factors['lead_status'] = lead_impact
        
        # Factor 2: Lead source
        source_impact = {'Referral': 20, 'Previous Client': 25, 'Website': 10, 'Walk-in': 5, 'Cold Call': -10}
        source_effect = source_impact.get(deal_data[5], 0)
        total_probability += source_effect
        probability_factors['lead_source'] = source_effect
        
        # Factor 3: Deal age
        try:
            deal_date = datetime.fromisoformat(deal_data[2].replace('Z', '+00:00').split('+')[0])
            days_old = (datetime.now() - deal_date).days
            
            if days_old <= 7:
                age_impact = 10
            elif days_old <= 30:
                age_impact = 0
            elif days_old <= 60:
                age_impact = -10
            else:
                age_impact = -20
                
            total_probability += age_impact
            probability_factors['deal_age'] = age_impact
            
        except (ValueError, AttributeError):
            probability_factors['deal_age'] = 0
        
        # Factor 4: Recent contact
        if deal_data[6]:  # last_contacted_date exists
            try:
                last_contact = datetime.fromisoformat(deal_data[6].replace('Z', '+00:00').split('+')[0])
                days_since_contact = (datetime.now() - last_contact).days
                
                if days_since_contact <= 3:
                    contact_impact = 15
                elif days_since_contact <= 7:
                    contact_impact = 5
                elif days_since_contact <= 14:
                    contact_impact = -5
                else:
                    contact_impact = -15
                    
                total_probability += contact_impact
                probability_factors['recent_contact'] = contact_impact
                
            except (ValueError, AttributeError):
                probability_factors['recent_contact'] = -10
        else:
            probability_factors['recent_contact'] = -10
        
        # Ensure probability is between 0 and 100
        total_probability = max(0, min(100, total_probability))
        
        # Generate recommendations
        recommendations = _generate_deal_recommendations(total_probability, probability_factors)
        
        conn.close()
        
        return {
            'deal_id': deal_id,
            'probability': round(total_probability, 1),
            'probability_factors': probability_factors,
            'confidence_level': _get_confidence_level(total_probability),
            'recommendations': recommendations
        }
        
    except Exception as e:
        logging.error(f"Error predicting deal probability: {str(e)}")
        return {'error': 'Failed to predict deal probability'}

def _generate_deal_recommendations(probability, factors) -> List[str]:
    """Generate recommendations to improve deal probability."""
    recommendations = []
    
    if probability < 40:
        recommendations.append("Deal at risk - immediate action required")
    elif probability < 60:
        recommendations.append("Moderate risk - increase engagement efforts")
    
    if factors.get('recent_contact', 0) < 0:
        recommendations.append("Contact the client immediately - communication gap detected")
    
    if factors.get('deal_age', 0) < -10:
        recommendations.append("Deal aging - create urgency or address concerns")
    
    if factors.get('lead_status', 0) < 0:
        recommendations.append("Lead status needs improvement - provide more value")
    
    if not recommendations:
        recommendations.append("Deal progressing well - maintain current momentum")
    
    return recommendations

def _get_confidence_level(probability) -> str:
    """Get confidence level based on probability."""
    if probability >= 80:
        return "Very High"
    elif probability >= 60:
        return "High"
    elif probability >= 40:
        return "Moderate"
    elif probability >= 20:
        return "Low"
    else:
        return "Very Low"
