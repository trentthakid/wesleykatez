"""
Knowledge base module for the Digital Twin real estate application.
Handles document processing, entity recognition, and information retrieval.
"""

import csv
import logging
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from database import get_db_connection

def find_properties_in_text(text: str) -> List[Dict[str, str]]:
    """
    Find property references in text using pattern matching and database lookup.
    Returns list of property dictionaries with building and unit information.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all properties from database
        cursor.execute("SELECT DISTINCT building, unit FROM Properties")
        all_properties = cursor.fetchall()
        
        found_properties = []
        text_lower = text.lower()
        
        # Check each property against the text
        for prop in all_properties:
            building, unit = prop[0], prop[1]
            
            # Create various search patterns
            patterns = [
                f"{building.lower()}.*{unit.lower()}",
                f"{building.lower()}.*unit.*{unit.lower()}",
                f"{building.lower()}.*#{unit.lower()}",
                f"unit.*{unit.lower()}.*{building.lower()}",
                f"{unit.lower()}.*{building.lower()}"
            ]
            
            # Check if any pattern matches
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if {'building': building, 'unit': unit} not in found_properties:
                        found_properties.append({'building': building, 'unit': unit})
                    break
        
        conn.close()
        return found_properties
        
    except Exception as e:
        logging.error(f"Error finding properties in text: {str(e)}")
        return []

def extract_contact_info_from_text(text: str) -> Dict[str, str]:
    """
    Extract contact information (email, phone) from text using regex patterns.
    """
    contact_info = {}
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['email'] = emails[0]  # Take first email found
    
    # Phone pattern (supports various formats including UAE numbers)
    phone_patterns = [
        r'\+971[-.\s]?\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}',  # UAE format
        r'\+\d{1,3}[-.\s]?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{4}',  # International
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Local format
        r'\b\d{10,12}\b'  # Simple number format
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
            break
    
    return contact_info

def extract_price_from_text(text: str) -> Optional[float]:
    """
    Extract price information from text.
    """
    # Price patterns (AED, USD, etc.)
    price_patterns = [
        r'AED\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*AED',
        r'\$\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'([0-9,]+(?:\.[0-9]{2})?)\s*million',
        r'([0-9,]+(?:\.[0-9]{2})?)\s*k',  # thousands
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text.replace(',', ''))
        if matches:
            try:
                price = float(matches[0])
                # Handle million/k suffixes
                if 'million' in text.lower():
                    price *= 1000000
                elif 'k' in text.lower():
                    price *= 1000
                return price
            except ValueError:
                continue
    
    return None

def add_to_knowledge_base(file_path: str, filename: str) -> bool:
    """
    Process an uploaded file and add its content to the knowledge base.
    """
    try:
        file_extension = filename.lower().split('.')[-1]

        if file_extension == 'csv':
            return add_contacts_from_csv(file_path, filename)

        # Extract content based on file type
        content = extract_content_from_file(file_path, filename)
        
        if not content:
            logging.warning(f"No content extracted from {filename}")
            return False
        
        # Determine content type
        content_type = get_content_type(file_extension)
        
        # Extract metadata
        metadata = extract_metadata_from_content(content, filename)
        
        # Store in knowledge base
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO KnowledgeNexus 
            (content_type, title, content, source_file, metadata, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            content_type,
            filename,
            content,
            filename,
            json.dumps(metadata),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Successfully added {filename} to knowledge base")
        return True
        
    except Exception as e:
        logging.error(f"Error adding {filename} to knowledge base: {str(e)}")
        return False

def extract_content_from_file(file_path: str, filename: str) -> str:
    """
    Extract text content from various file types.
    """
    try:
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension in ['txt', 'csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        elif file_extension == 'pdf':
            return extract_pdf_content(file_path)
        
        elif file_extension in ['doc', 'docx']:
            return extract_word_content(file_path)
        
        elif file_extension in ['xls', 'xlsx']:
            return extract_excel_content(file_path)
        
        else:
            # Try to read as text file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
    except Exception as e:
        logging.error(f"Error extracting content from {filename}: {str(e)}")
        return ""

def extract_pdf_content(file_path: str) -> str:
    """
    Extract text content from PDF files.
    Note: This is a basic implementation. For production, consider using PyPDF2 or pdfplumber.
    """
    try:
        # For now, return placeholder since we don't have PDF libraries
        # In production, you would use:
        # import PyPDF2 or pdfplumber
        logging.warning(f"PDF extraction not implemented for {file_path}")
        return f"PDF file uploaded: {os.path.basename(file_path)}"
    except Exception as e:
        logging.error(f"Error extracting PDF content: {str(e)}")
        return ""

def extract_word_content(file_path: str) -> str:
    """
    Extract text content from Word documents.
    Note: This is a basic implementation. For production, consider using python-docx.
    """
    try:
        # For now, return placeholder since we don't have docx libraries
        logging.warning(f"Word document extraction not implemented for {file_path}")
        return f"Word document uploaded: {os.path.basename(file_path)}"
    except Exception as e:
        logging.error(f"Error extracting Word content: {str(e)}")
        return ""

def extract_excel_content(file_path: str) -> str:
    """
    Extract text content from Excel files.
    Note: This is a basic implementation. For production, consider using pandas or openpyxl.
    """
    try:
        # For now, return placeholder since we don't have excel libraries
        logging.warning(f"Excel extraction not implemented for {file_path}")
        return f"Excel file uploaded: {os.path.basename(file_path)}"
    except Exception as e:
        logging.error(f"Error extracting Excel content: {str(e)}")
        return ""

def get_content_type(file_extension: str) -> str:
    """
    Determine content type based on file extension.
    """
    content_type_mapping = {
        'pdf': 'document',
        'doc': 'document',
        'docx': 'document',
        'txt': 'text',
        'csv': 'data',
        'xls': 'spreadsheet',
        'xlsx': 'spreadsheet',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image'
    }
    
    return content_type_mapping.get(file_extension, 'unknown')

def extract_metadata_from_content(content: str, filename: str) -> Dict[str, Any]:
    """
    Extract metadata from content including properties, contacts, and prices.
    """
    metadata = {
        'filename': filename,
        'word_count': len(content.split()),
        'char_count': len(content),
        'extraction_date': datetime.now().isoformat()
    }
    
    # Find properties mentioned
    properties = find_properties_in_text(content)
    if properties:
        metadata['properties_mentioned'] = properties
    
    # Find contact information
    contact_info = extract_contact_info_from_text(content)
    if contact_info:
        metadata['contact_info'] = contact_info
    
    # Find prices
    price = extract_price_from_text(content)
    if price:
        metadata['price_mentioned'] = price
    
    # Extract key terms (simple keyword extraction)
    key_terms = extract_key_terms(content)
    if key_terms:
        metadata['key_terms'] = key_terms
    
    return metadata

def extract_key_terms(content: str) -> List[str]:
    """
    Extract key terms from content using simple frequency analysis.
    """
    try:
        # Real estate specific keywords
        real_estate_terms = [
            'apartment', 'villa', 'penthouse', 'townhouse', 'studio',
            'bedroom', 'bathroom', 'sqft', 'square feet', 'balcony',
            'parking', 'gym', 'pool', 'garden', 'view', 'furnished',
            'lease', 'rent', 'sale', 'buy', 'investment', 'mortgage',
            'dubai', 'abu dhabi', 'sharjah', 'palm jumeirah', 'downtown',
            'marina', 'jbr', 'business bay', 'difc', 'deira'
        ]
        
        content_lower = content.lower()
        found_terms = []
        
        for term in real_estate_terms:
            if term in content_lower:
                found_terms.append(term)
        
        return found_terms[:10]  # Return top 10 terms
        
    except Exception as e:
        logging.error(f"Error extracting key terms: {str(e)}")
        return []

def search_knowledge_base(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search the knowledge base for relevant content.
    This is a simple text-based search. For production, consider implementing semantic search.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simple text search using LIKE
        search_terms = query.lower().split()
        
        # Build search query
        search_conditions = []
        search_params = []
        
        for term in search_terms:
            search_conditions.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ? OR LOWER(metadata) LIKE ?)")
            search_params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
        
        search_query = f"""
            SELECT id, content_type, title, content, source_file, metadata, created_date
            FROM KnowledgeNexus
            WHERE {' AND '.join(search_conditions)}
            ORDER BY created_date DESC
            LIMIT ?
        """
        search_params.append(limit)
        
        cursor.execute(search_query, search_params)
        results = cursor.fetchall()
        
        knowledge_items = []
        for row in results:
            try:
                metadata = json.loads(row[5]) if row[5] else {}
            except json.JSONDecodeError:
                metadata = {}
            
            knowledge_items.append({
                'id': row[0],
                'content_type': row[1],
                'title': row[2],
                'content_preview': row[3][:200] + "..." if len(row[3]) > 200 else row[3],
                'source_file': row[4],
                'metadata': metadata,
                'created_date': row[6]
            })
        
        conn.close()
        return knowledge_items
        
    except Exception as e:
        logging.error(f"Error searching knowledge base: {str(e)}")
        return []

def get_relevant_context(query: str) -> str:
    """
    Get relevant context from knowledge base for AI responses.
    """
    try:
        # Search knowledge base
        relevant_items = search_knowledge_base(query, limit=3)
        
        if not relevant_items:
            return "No relevant documents found in knowledge base."
        
        context = "Relevant information from knowledge base:\n\n"
        
        for item in relevant_items:
            context += f"Document: {item['title']}\n"
            context += f"Content: {item['content_preview']}\n"
            
            # Add property information if available
            if 'properties_mentioned' in item['metadata']:
                properties = item['metadata']['properties_mentioned']
                if properties:
                    property_list = [f"{p['building']} Unit {p['unit']}" for p in properties]
                    context += f"Properties mentioned: {', '.join(property_list)}\n"
            
            context += "\n"
        
        return context
        
    except Exception as e:
        logging.error(f"Error getting relevant context: {str(e)}")
        return "Error retrieving context from knowledge base."

def update_knowledge_item_tags(item_id: int, tags: List[str]) -> bool:
    """
    Update tags for a knowledge base item.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tags_str = ','.join(tags)
        
        cursor.execute("""
            UPDATE KnowledgeNexus 
            SET tags = ?, updated_date = ?
            WHERE id = ?
        """, (tags_str, datetime.now().isoformat(), item_id))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logging.error(f"Error updating knowledge item tags: {str(e)}")
        return False

def add_contacts_from_csv(file_path: str, filename: str) -> bool:
    """
    Process a CSV file and add its content to the Contacts table.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader)  # Read header row
            
            # Check if the header matches the expected format for contacts
            if header != ['name', 'email', 'phone', 'lead_status']:
                logging.info(f"{filename} is not a contacts CSV file. Adding to knowledge base instead.")
                return False

            conn = get_db_connection()
            cursor = conn.cursor()
            
            for row in reader:
                cursor.execute("""
                    INSERT INTO Contacts (name, email, phone, lead_status, source, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (row[0], row[1], row[2], row[3], filename, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Successfully added contacts from {filename}")
            return True
            
    except Exception as e:
        logging.error(f"Error adding contacts from {filename}: {str(e)}")
        return False

def get_knowledge_statistics() -> Dict[str, Any]:
    """
    Get statistics about the knowledge base.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total items
        cursor.execute("SELECT COUNT(*) FROM KnowledgeNexus")
        total_items = cursor.fetchone()[0]
        
        # Items by content type
        cursor.execute("""
            SELECT content_type, COUNT(*) 
            FROM KnowledgeNexus 
            GROUP BY content_type
        """)
        
        content_types = {}
        for row in cursor.fetchall():
            content_types[row[0]] = row[1]
        
        # Recent additions (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM KnowledgeNexus 
            WHERE created_date >= ?
        """, (seven_days_ago,))
        
        recent_additions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_items': total_items,
            'content_types': content_types,
            'recent_additions': recent_additions,
            'last_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting knowledge statistics: {str(e)}")
        return {'error': 'Failed to get knowledge statistics'}
