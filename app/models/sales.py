# """
# Sales Lead Model - FastAPI
# File: app/models/sales.py

# Converted from Django model with exact field matching.
# """
# from sqlalchemy import Column, Integer, String, Text, DateTime
# from sqlalchemy.sql import func
# from app.database import Base


# class SalesLead(Base):
#     """
#     Sales Lead model - matches Django SalesLead exactly.
    
#     Status choices:
#         - new: New lead
#         - contacted: Initial contact made
#         - qualified: Lead qualified for sales
#         - proposal: Proposal sent
#         - won: Deal won
#         - lost: Deal lost
#     """
#     __tablename__ = "sales_lead"
    
#     # Primary key
#     id = Column(Integer, primary_key=True, index=True)
    
#     # Required fields
#     company_name = Column(String(255), nullable=False, index=True)
#     owner = Column(String(255), nullable=False)
    
#     # Email - CRITICAL: nullable=True to match Django's flexible validation
#     # Django allows invalid emails like 'me@123' in the database
#     email = Column(String(255), nullable=True)
    
#     # Status with default
#     status = Column(String(20), default="new", nullable=False, index=True)
    
#     # Optional contact fields
#     phone = Column(String(50), nullable=True)
#     website = Column(String(255), nullable=True)
    
#     # Optional company details
#     location = Column(String(255), nullable=True)
#     founding_year = Column(String(20), nullable=True)
#     funding_status = Column(String(100), nullable=True)
#     segment = Column(String(255), nullable=True)
    
#     # Point of contact
#     poc = Column(String(255), nullable=True)
#     poc_email = Column(String(255), nullable=True)
    
#     # Notes
#     notes = Column(Text, nullable=True)
    
#     # Timestamp
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
#     def __repr__(self):
#         return f"<SalesLead(id={self.id}, company='{self.company_name}', status='{self.status}')>"


"""
Sales Lead Model - FastAPI (OPTIMIZED)
File: app/models/sales.py

Added indexes for performance with thousands of records.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class SalesLead(Base):
    """
    Sales Lead model - optimized for performance.
    
    Status choices:
        - new: New lead
        - contacted: Initial contact made
        - qualified: Lead qualified for sales
        - proposal: Proposal sent
        - won: Deal won
        - lost: Deal lost
        - converted: Converted to customer
    """
    __tablename__ = "sales_lead"
    
    # Primary key (automatically indexed)
    id = Column(Integer, primary_key=True, index=True)
    
    # Required fields with indexes for filtering/searching
    company_name = Column(String(255), nullable=False, index=True)  # Search by company
    owner = Column(String(255), nullable=False, index=True)  # Filter by owner
    
    # Email - nullable to match Django's flexible validation
    email = Column(String(255), nullable=True, index=True)  # Search/filter by email
    
    # Status with index for filtering (most common query)
    status = Column(String(20), default="new", nullable=False, index=True)
    
    # Optional contact fields
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Company details
    location = Column(String(255), nullable=True, index=True)  # Filter by location
    founding_year = Column(String(20), nullable=True)
    funding_status = Column(String(100), nullable=True)
    segment = Column(String(255), nullable=True, index=True)  # Filter by segment
    
    # Point of contact
    poc = Column(String(255), nullable=True)
    poc_email = Column(String(255), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamp with index for sorting
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Most common: filter by status + sort by date
        Index('idx_status_created', 'status', 'created_at'),
        # Search by company + status
        Index('idx_company_status', 'company_name', 'status'),
        # Filter by location + status
        Index('idx_location_status', 'location', 'status'),
    )
    
    def __repr__(self):
        return f"<SalesLead(id={self.id}, company='{self.company_name}', status='{self.status}')>"