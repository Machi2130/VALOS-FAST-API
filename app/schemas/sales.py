"""
Sales Lead Schemas - FastAPI
File: app/schemas/sales.py

Pydantic models for request/response validation.
CRITICAL: Uses Optional[str] for email instead of EmailStr to match Django's flexibility.
"""
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


# Valid status choices (matching Django)
VALID_STATUSES = ["new", "contacted", "qualified", "proposal", "won", "lost", "converted"]


class SalesLeadBase(BaseModel):
    """Base schema with common fields"""
    company_name: str
    owner: str
    
    # CRITICAL: Use Optional[str] instead of EmailStr
    # Django allows invalid emails like 'me@123' in database
    email: Optional[str] = None
    
    status: str = "new"
    phone: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    founding_year: Optional[str] = None
    funding_status: Optional[str] = None
    segment: Optional[str] = None
    poc: Optional[str] = None
    poc_email: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values"""
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v
    
    @field_validator('email', 'poc_email')
    @classmethod
    def clean_email(cls, v: Optional[str]) -> Optional[str]:
        """Clean email field - allow empty strings as None"""
        if v is not None and v.strip() == '':
            return None
        return v


class SalesLeadCreate(SalesLeadBase):
    """Schema for creating a new sales lead"""
    pass


class SalesLeadUpdate(BaseModel):
    """Schema for updating a sales lead (all fields optional)"""
    company_name: Optional[str] = None
    owner: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    founding_year: Optional[str] = None
    funding_status: Optional[str] = None
    segment: Optional[str] = None
    poc: Optional[str] = None
    poc_email: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status if provided"""
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v


class SalesLeadStatusUpdate(BaseModel):
    """Schema for updating only the status"""
    status: str
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value"""
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v


class SalesLeadResponse(SalesLeadBase):
    """Schema for API responses (includes database fields)"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "company_name": "Tech Innovations Ltd",
                "owner": "John Doe",
                "email": "contact@techinnovations.com",
                "status": "contacted",
                "phone": "+1-555-0123",
                "website": "https://techinnovations.com",
                "location": "San Francisco, CA",
                "founding_year": "2020",
                "funding_status": "Series A",
                "segment": "B2B SaaS",
                "poc": "Jane Smith",
                "poc_email": "jane@techinnovations.com",
                "notes": "Interested in enterprise plan",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )


def is_valid_status(status: str) -> bool:
    """Helper function to check if status is valid"""
    return status in VALID_STATUSES