"""
Gemini integration module for the Digital Twin real estate application.
Handles all interactions with Google's Gemini AI models.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types

class GeminiClient:
    """
    Client for interacting with Google Gemini AI models.
    Provides methods for text generation, analysis, and real estate specific tasks.
    """
    
    def __init__(self):
        """Initialize the Gemini client with API key from environment."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logging.info("Gemini client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Gemini client: {str(e)}")
                self.client = None
    
    def generate_response(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """
        Generate a response using Gemini model.
        
        Args:
            prompt: The input prompt for the model
            model: The Gemini model to use (default: gemini-2.5-flash)
            
        Returns:
            Generated response text
        """
        if not self.client:
            return "I'm sorry, but I'm currently unable to process your request. Please check that the Gemini API key is properly configured."
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            
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
        if not self.client:
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
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
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
You are a professional real estate copywriter. Create a compelling property description based on the following information:

Property Details:
- Building: {property_data.get('building', 'N/A')}
- Unit: {property_data.get('unit', 'N/A')}
- Type: {property_data.get('property_type', 'N/A')}
- Bedrooms: {property_data.get('bedrooms', 'N/A')}
- Bathrooms: {property_data.get('bathrooms', 'N/A')}
- Size: {property_data.get('size_sqft', 'N/A')} sqft
- Price: AED {property_data.get('price', 'N/A'):,.0f} if isinstance(property_data.get('price'), (int, float)) else 'N/A'
- Area: {property_data.get('area', 'N/A')}
- Amenities: {property_data.get('amenities', 'N/A')}

Write a professional, engaging property description that:
1. Highlights the key features and benefits
2. Mentions the location advantages
3. Uses persuasive language to attract potential buyers/tenants
4. Is approximately 150-250 words
5. Includes a compelling opening line

Focus on lifestyle benefits and investment potential where appropriate.
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
You are a real estate market analyst. Analyze the following market data and provide insights:

Market Data:
{json.dumps(market_data, indent=2)}

Please provide:
1. Key trends in the market
2. Price movements and patterns
3. Investment opportunities
4. Market outlook
5. Recommendations for buyers and sellers

Keep the analysis professional and data-driven, suitable for real estate professionals.
"""
        
        return self.generate_response(prompt, model="gemini-2.5-pro")
    
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
You are a professional real estate agent. Write a personalized follow-up email based on the following information:

Contact Information:
{json.dumps(contact_info, indent=2)}

Context: {context}

Write a professional, warm, and personalized email that:
1. References our previous interaction
2. Provides value (market insights, property suggestions, etc.)
3. Has a clear call-to-action
4. Maintains a professional but friendly tone
5. Is concise (under 200 words)

Include both subject line and email body.
Format as:
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
Summarize the following conversation between a real estate agent and client:

{conversation_text}

Provide a concise summary that includes:
1. Client's requirements and preferences
2. Properties discussed
3. Key decisions or next steps
4. Important dates or deadlines
5. Action items for follow-up

Keep the summary professional and actionable.
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
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
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
    
    def is_available(self) -> bool:
        """
        Check if the Gemini client is available and working.
        
        Returns:
            True if client is available, False otherwise
        """
        return self.client is not None
