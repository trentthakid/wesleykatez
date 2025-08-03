"""
Gemini integration module for the Digital Twin real estate application.
Handles all interactions with Google's Gemini AI models.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from google.generativeai import types

class GeminiClient:
    """
    Client for interacting with Google Gemini AI models.
    Provides methods for text generation, analysis, and real estate specific tasks.
    """
    
    def __init__(self):
        """Initialize the Gemini client with API key from environment."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.warning("GEMINI_API_KEY not found in environment variables. Please set the environment variable.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                logging.info("Gemini client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Gemini client: {str(e)}")
                self.model = None
    
    def generate_response(self, prompt: str, model: str = "gemini-1.5-flash") -> str:
        """
        Generate a response using Gemini model.
        
        Args:
            prompt: The input prompt for the model
            model: The Gemini model to use (default: gemini-1.5-flash)
            
        Returns:
            Generated response text
        """
        if not self.model:
            return "I'm sorry, but I'm currently unable to process your request. Please check that the Gemini API key is properly configured."
        
        try:
            response = self.model.generate_content(prompt)
            
            return response.text if response.text else "I couldn't generate a response for that query."
            
        except Exception as e:
            logging.error(f"Error generating Gemini response: {str(e)}")
            return "I encountered an error while processing your request. Please try again or contact support."
    
    def analyze_real_estate_document(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze a real estate document and extract key information.
        
        Args:
            document_text: The text content of the document
            
        Returns:
            Dictionary containing extracted information
        """
        if not self.model:
            return {"error": "Gemini client not available"}
        
        prompt = f"""
You are a real estate AI assistant specializing in document analysis. Analyze the following real estate document and extract key information in JSON format.

Document text:
{document_text}

Please extract and return the following information in JSON format:
{{
    "document_type": "contract/listing/brochure/report/other",
    "properties": [
        {{
            "building": "building name",
            "unit": "unit number",
            "property_type": "apartment/villa/office/etc",
            "bedrooms": number,
            "bathrooms": number,
            "size_sqft": number,
            "price": number,
            "area": "location/area name"
        }}
    ],
    "contacts": [
        {{
            "name": "contact name",
            "role": "buyer/seller/agent/owner",
            "email": "email address",
            "phone": "phone number"
        }}
    ],
    "key_dates": [
        {{
            "date": "YYYY-MM-DD",
            "description": "what happens on this date"
        }}
    ],
    "financial_details": {{
        "total_value": number,
        "commission": number,
        "deposit": number,
        "monthly_payment": number
    }},
    "important_terms": ["list of important terms or conditions"],
    "summary": "brief summary of the document"
}}

Only include information that is clearly stated in the document. Use null for missing information.
"""
        
        try:
            model_to_use = genai.GenerativeModel("gemini-1.5-pro")
            response = model_to_use.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return {"error": "No response generated"}
                
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response from Gemini")
            return {"error": "Invalid JSON response"}
        except Exception as e:
            logging.error(f"Error analyzing document with Gemini: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def generate_property_description(self, property_data: Dict[str, Any]) -> str:
        """
        Generate a compelling property description.
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            Generated property description
        """
        prompt = f"""
You are AURA, drafting a property listing for Wesley Kateguru, a top agent specializing in luxury properties on the Palm Jumeirah.
The description must reflect his professional brand: sophisticated, detailed, and focused on unique value propositions for high-net-worth clients.
The target audience appreciates specifics and lifestyle benefits. The description will be used on platforms like Property Finder and Bayut.

**Wesley's Expert Knowledge to Incorporate:**
- For villas on the fronds, mention the value of the view (e.g., "sought-after sunset views of the Marina skyline" for even-numbered villas, "serene sunrise views" for odd-numbered villas).
- Highlight proximity to key landmarks like Nakheel Mall, The Pointe, or specific beach clubs.
- If it's a bespoke/custom villa, emphasize its uniqueness compared to standard Nakheel villas.

**Property Details:**
- Building/Villa Type: {property_data.get('building', 'N/A')}
- Unit/Villa Number: {property_data.get('unit', 'N/A')}
- Property Type: {property_data.get('property_type', 'N/A')}
- Bedrooms: {property_data.get('bedrooms', 'N/A')}
- Bathrooms: {property_data.get('bathrooms', 'N/A')}
- Size: {property_data.get('size_sqft', 'N/A')} sqft
- Price: AED {property_data.get('price', 'N/A'):,.0f} if isinstance(property_data.get('price'), (int, float)) else 'N/A'
- Area: {property_data.get('area', 'N/A')}
- Amenities: {property_data.get('amenities', 'N/A')}

**Task:**
Write a professional, engaging property description (150-250 words) that:
1.  Starts with a powerful opening line that captures the essence of the property.
2.  Weaves in the expert knowledge points mentioned above where applicable.
3.  Highlights 2-3 unique selling points (e.g., specific upgrades, rare layout, view).
4.  Uses sophisticated and persuasive language.
5.  Ends with a clear call to action to contact Wesley Kateguru for a private viewing.
"""
        
        return self.generate_response(prompt)
    
    def analyze_market_trends(self, market_data: List[Dict[str, Any]]) -> str:
        """
        Analyze market trends and provide insights.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Market analysis and insights
        """
        prompt = f"""
You are AURA, acting as a senior market analyst for Wesley Kateguru, a Palm Jumeirah specialist.
Your analysis must be data-driven, objective, and tailored for Wesley's use in advising high-net-worth clients.
The focus should be on identifying actionable insights for the Palm Jumeirah market.

**Expert Knowledge to Apply:**
- Reference specific zones (Trunk, Fronds, Crescent) and property types (e.g., Signature Villas vs. Garden Homes, branded vs. non-branded residences).
- Correlate trends with known market drivers (e.g., new developments like Atlantis The Royal, infrastructure like the Palm Monorail).

**Market Data Provided:**
{json.dumps(market_data, indent=2)}

**Task:**
Generate a concise, professional market analysis report. Structure it as follows:
1.  **Executive Summary:** A brief, high-level overview of the current market state on Palm Jumeirah.
2.  **Key Trends:** 3-4 bullet points on the most significant current trends (e.g., "Increasing demand for bespoke villas on the fronds," "Price stabilization in Trunk apartments").
3.  **Price Analysis:** Note any significant price movements, including percentage changes if possible. Highlight which segments are overperforming or underperforming.
4.  **Investment Opportunities:** Identify 1-2 specific, actionable investment opportunities for Wesley's clients (e.g., "Look for undervalued Garden Homes on lower-numbered fronds for renovation potential," "Consider branded residences on the Crescent for strong rental yields").
5.  **Market Outlook:** A brief forward-looking statement on what to expect in the next quarter.
6.  **Client Recommendations:** Separate, concise advice for potential buyers and sellers in the current market.
"""
        
        return self.generate_response(prompt, model="gemini-1.5-pro")
    
    def generate_follow_up_email(self, contact_info: Dict[str, Any], context: str = "") -> str:
        """
        Generate a personalized follow-up email.
        
        Args:
            contact_info: Contact information and preferences
            context: Additional context about the interaction
            
        Returns:
            Generated email content
        """
        prompt = f"""
You are AURA, drafting a follow-up email on behalf of Wesley Kateguru.
Your goal is to save him time while maintaining his professional and personal touch. The tone should be warm, professional, and action-oriented.

**Contact Information:**
{json.dumps(contact_info, indent=2)}

**Context of Last Interaction:**
{context}

**Task:**
Draft a concise and effective follow-up email (under 150 words).
1.  **Subject Line:** Create a compelling subject line that is personalized and likely to be opened.
2.  **Email Body:**
    -   Start with a warm, personal greeting.
    -   Briefly reference your last conversation (e.g., "It was a pleasure speaking with you about...").
    -   Provide immediate value. This could be a link to a relevant new listing, a brief market insight about Palm Jumeirah, or an answer to a question they had.
    -   Include a clear and easy call-to-action (e.g., "Are you available for a brief call tomorrow to discuss?", "I have a few properties I think you'll love, when is a good time to view them?").
    -   Sign off as Wesley Kateguru.

**Format:**
Subject: [subject line]

[email body]
"""
        
        return self.generate_response(prompt)
    
    def create_comparative_market_analysis(self, target_property: Dict[str, Any], comparable_properties: List[Dict[str, Any]]) -> str:
        """
        Create a comparative market analysis (CMA).
        
        Args:
            target_property: The property being analyzed
            comparable_properties: List of comparable properties
            
        Returns:
            CMA report
        """
        prompt = f"""
You are a real estate valuation expert. Create a Comparative Market Analysis (CMA) report.

Target Property:
{json.dumps(target_property, indent=2)}

Comparable Properties:
{json.dumps(comparable_properties, indent=2)}

Create a professional CMA report that includes:
1. Executive summary
2. Property overview
3. Comparable sales analysis
4. Market trends affecting value
5. Recommended pricing strategy
6. Supporting rationale

Format the report professionally with clear sections and bullet points where appropriate.
"""
        
        return self.generate_response(prompt, model="gemini-2.5-pro")
    
    def generate_investment_analysis(self, property_data: Dict[str, Any], financial_assumptions: Dict[str, Any]) -> str:
        """
        Generate an investment analysis for a property.
        
        Args:
            property_data: Property information
            financial_assumptions: Financial parameters for analysis
            
        Returns:
            Investment analysis report
        """
        prompt = f"""
You are a real estate investment analyst. Create an investment analysis report.

Property Information:
{json.dumps(property_data, indent=2)}

Financial Assumptions:
{json.dumps(financial_assumptions, indent=2)}

Create a comprehensive investment analysis that includes:
1. Investment summary
2. Cash flow projections
3. Return on investment calculations
4. Risk assessment
5. Market factors
6. Investment recommendation

Use professional financial terminology and provide clear recommendations.
"""
        
        return self.generate_response(prompt, model="gemini-2.5-pro")
    
    def summarize_conversation(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Summarize a conversation with a client.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            Conversation summary
        """
        conversation_text = "\n".join([
            f"{msg.get('sender', 'Unknown')}: {msg.get('message', '')}" 
            for msg in conversation_history
        ])
        
        prompt = f"""
You are AURA, Wesley Kateguru's assistant manager. Your task is to create a concise, actionable summary of a client conversation for Wesley's review.
The summary should be structured for quick reading and decision-making.

**Conversation Text:**
{conversation_text}

**Task:**
Provide a summary in the following format:
- **Client Requirements:** (e.g., 3-bedroom villa on Palm Jumeirah, budget AED 10M, sunset view preferred)
- **Properties Discussed:** (e.g., Signature Villa, Frond K; Garden Home, Frond M)
- **Key Outcomes/Decisions:** (e.g., Client is interested in viewing the Frond K villa)
- **Action Items for Wesley:** (e.g., "Call client tomorrow to schedule viewing," "Prepare CMA for Frond M villa")
- **Urgency/Sentiment:** (e.g., High urgency, client is ready to buy)

Keep the summary professional and focused on what Wesley needs to do next.
"""
        
        return self.generate_response(prompt)
    
    def extract_client_preferences(self, conversation_text: str) -> Dict[str, Any]:
        """
        Extract client preferences from conversation text.
        
        Args:
            conversation_text: Text of client conversation
            
        Returns:
            Dictionary of extracted preferences
        """
        prompt = f"""
Extract client preferences from the following conversation and return them in JSON format:

{conversation_text}

Extract and return the following information in JSON format:
{{
    "budget_range": {{
        "min": number,
        "max": number,
        "currency": "AED/USD/etc"
    }},
    "property_type": ["apartment", "villa", "office", "etc"],
    "preferred_areas": ["area1", "area2", "etc"],
    "bedrooms": {{
        "min": number,
        "max": number
    }},
    "bathrooms": {{
        "min": number,
        "max": number
    }},
    "size_requirements": {{
        "min_sqft": number,
        "max_sqft": number
    }},
    "amenities": ["gym", "pool", "parking", "etc"],
    "timeline": "urgent/flexible/specific date",
    "investment_purpose": "personal use/rental income/capital appreciation",
    "financing": "cash/mortgage/other",
    "special_requirements": ["furnished", "pet-friendly", "etc"]
}}

Only include information that is clearly stated. Use null for missing information.
"""
        
        try:
            model_to_use = genai.GenerativeModel("gemini-1.5-pro")
            response = model_to_use.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return {}
                
        except Exception as e:
            logging.error(f"Error extracting client preferences: {str(e)}")
            return {}
    
    def get_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Determine the user's intent from a single user message.
        """
        prompt = f"""
You are AURA, an AI assistant manager for a real estate agent. Your primary job is to understand the user's command, identify their intent, and extract key information (entities).

**User Command:**
"{user_input}"

**Task:**
Analyze the user's command and determine the intent.
Return a single JSON object with the `intent` and any `entities`.

**Possible Intents & Examples:**
- `find_owner`: "who owns shoreline unit 505?", "get me the owner of frond p villa 22"
- `create_task`: "remind me to call ahmed tomorrow at 10am", "add a viewing for atlantis royal penthouse on friday"
- `create_contact`: "new contact: John Smith, john@email.com, +971501234567", "add Jane Doe to my contacts"
- `get_follow_ups`: "who do i need to follow up with?", "show me my follow ups"
- `score_leads`: "score my leads", "who are my hottest leads right now?"
- `find_buyers`: "find buyers for shoreline apartment 1203", "who is looking for a 4 bed garden home?"
- `search_properties`: "show me available 3 bed apartments in oceana", "search for villas on frond g under 15M"
- `get_market_analysis`: "what are the latest market trends on the palm?", "give me a market analysis for the crescent"
- `get_performance_summary`: "how am i doing this month?", "show me my performance"
- `get_daily_briefing`: "what's my daily briefing?", "give me the rundown for today"
- `unknown`: Use this if the intent is unclear or doesn't fit any other category.

**Example Output Format:**
{{
  "intent": "create_task",
  "entities": {{
    "task_description": "call ahmed tomorrow at 10am",
    "due_date": "2025-08-03T10:00:00"
  }}
}}

Now, based on the user command provided, what is the intent?
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return {"intent": "unknown", "entities": {}}
                
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response from Gemini")
            return {"intent": "unknown", "entities": {}}
        except Exception as e:
            logging.error(f"Error getting intent with Gemini: {str(e)}")
            return {"intent": "unknown", "entities": {}}

    def is_available(self) -> bool:
        """
        Check if the Gemini client is available and working.
        
        Returns:
            True if client is available, False otherwise
        """
        return self.model is not None
