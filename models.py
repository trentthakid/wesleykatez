"""
Data models and database utilities for the Digital Twin application.
This module defines the structure and relationships between different entities.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

@dataclass
class Property:
    """Represents a real estate property"""
    id: Optional[int] = None
    building: str = ""
    unit: str = ""
    area: str = ""
    property_type: str = ""
    bedrooms: int = 0
    bathrooms: int = 0
    size_sqft: float = 0.0
    price: float = 0.0
    status: str = "Available"
    description: str = ""
    amenities: str = ""
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert property to dictionary"""
        return {
            'id': self.id,
            'building': self.building,
            'unit': self.unit,
            'area': self.area,
            'property_type': self.property_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'size_sqft': self.size_sqft,
            'price': self.price,
            'status': self.status,
            'description': self.description,
            'amenities': self.amenities,
            'created_date': self.created_date,
            'updated_date': self.updated_date
        }

@dataclass
class Contact:
    """Represents a client or prospect"""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    lead_status: str = "Cold"
    source: str = ""
    notes: str = ""
    last_contacted_date: Optional[str] = None
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert contact to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'lead_status': self.lead_status,
            'source': self.source,
            'notes': self.notes,
            'last_contacted_date': self.last_contacted_date,
            'created_date': self.created_date,
            'updated_date': self.updated_date
        }

@dataclass
class Deal:
    """Represents a real estate transaction"""
    id: Optional[int] = None
    property_id: Optional[int] = None
    contact_id: Optional[int] = None
    deal_type: str = ""
    status: str = "Active"
    deal_value: float = 0.0
    commission: float = 0.0
    created_date: Optional[str] = None
    closing_date: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert deal to dictionary"""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'contact_id': self.contact_id,
            'deal_type': self.deal_type,
            'status': self.status,
            'deal_value': self.deal_value,
            'commission': self.commission,
            'created_date': self.created_date,
            'closing_date': self.closing_date,
            'notes': self.notes
        }

@dataclass
class Task:
    """Represents a task or todo item"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    status: str = "Pending"
    priority: str = "Medium"
    assigned_to: str = ""
    contact_id: Optional[int] = None
    property_id: Optional[int] = None
    created_date: Optional[str] = None
    due_date: Optional[str] = None
    completed_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'contact_id': self.contact_id,
            'property_id': self.property_id,
            'created_date': self.created_date,
            'due_date': self.due_date,
            'completed_date': self.completed_date
        }

@dataclass
class ContactProperty:
    """Represents the relationship between a contact and property"""
    id: Optional[int] = None
    contact_id: int = 0
    property_id: int = 0
    relationship_type: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_date: Optional[str] = None

@dataclass
class KnowledgeItem:
    """Represents an item in the knowledge base"""
    id: Optional[int] = None
    content_type: str = ""
    title: str = ""
    content: str = ""
    embedding_vector: Optional[bytes] = None
    source_file: str = ""
    metadata: str = ""
    tags: str = ""
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

    def get_metadata_dict(self) -> Dict[str, Any]:
        """Parse metadata JSON string to dictionary"""
        try:
            return json.loads(self.metadata) if self.metadata else {}
        except json.JSONDecodeError:
            return {}

    def set_metadata_dict(self, metadata_dict: Dict[str, Any]):
        """Set metadata from dictionary"""
        self.metadata = json.dumps(metadata_dict)

@dataclass
class LeadScore:
    """Represents a lead scoring entry"""
    id: Optional[int] = None
    contact_id: int = 0
    score: int = 0
    score_factors: str = ""
    last_calculated: Optional[str] = None

    def get_factors_dict(self) -> Dict[str, Any]:
        """Parse score factors JSON string to dictionary"""
        try:
            return json.loads(self.score_factors) if self.score_factors else {}
        except json.JSONDecodeError:
            return {}

    def set_factors_dict(self, factors_dict: Dict[str, Any]):
        """Set score factors from dictionary"""
        self.score_factors = json.dumps(factors_dict)

# Utility functions for working with models

def create_property_from_row(row) -> Property:
    """Create Property object from database row"""
    return Property(
        id=row[0] if row else None,
        building=row[1] if len(row) > 1 else "",
        unit=row[2] if len(row) > 2 else "",
        area=row[3] if len(row) > 3 else "",
        property_type=row[4] if len(row) > 4 else "",
        bedrooms=row[5] if len(row) > 5 else 0,
        bathrooms=row[6] if len(row) > 6 else 0,
        size_sqft=row[7] if len(row) > 7 else 0.0,
        price=row[8] if len(row) > 8 else 0.0,
        status=row[9] if len(row) > 9 else "Available",
        description=row[10] if len(row) > 10 else "",
        amenities=row[11] if len(row) > 11 else "",
        created_date=row[12] if len(row) > 12 else None,
        updated_date=row[13] if len(row) > 13 else None
    )

def create_contact_from_row(row) -> Contact:
    """Create Contact object from database row"""
    return Contact(
        id=row[0] if row else None,
        name=row[1] if len(row) > 1 else "",
        email=row[2] if len(row) > 2 else "",
        phone=row[3] if len(row) > 3 else "",
        lead_status=row[4] if len(row) > 4 else "Cold",
        source=row[5] if len(row) > 5 else "",
        notes=row[6] if len(row) > 6 else "",
        last_contacted_date=row[7] if len(row) > 7 else None,
        created_date=row[8] if len(row) > 8 else None,
        updated_date=row[9] if len(row) > 9 else None
    )
