"""
Costing Models - FastAPI (OPTIMIZED)
File: app/models/costing.py

Added indexes for performance optimization.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PackagingOption(Base):
    __tablename__ = "packaging_option"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)  # Search by name
    cost = Column(Numeric(12, 2), default=0.00, nullable=False)
    
    # Relationships
    costings = relationship("Costing", secondary="costing_packaging", back_populates="packaging")
    
    def __repr__(self):
        return f"<PackagingOption {self.name}>"


class Costing(Base):
    __tablename__ = "costing"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Required fields with indexes for searching/filtering
    project_code = Column(String(16), index=True, nullable=False)  # Filter by project
    product_name = Column(String(255), nullable=False, index=True)  # Search by product
    
    # SKU and raw material
    sku_ml = Column(Numeric(12, 3), nullable=True)
    rm_per_litre = Column(Numeric(12, 4), nullable=True)
    
    # Packaging
    packaging_other = Column(String(255), nullable=True)
    packaging_cost_manual = Column(Numeric(12, 2), nullable=True)
    
    # Defaults (editable)
    batch_size_kg = Column(Numeric(12, 2), default=500.00, nullable=False)
    gst_percent = Column(Numeric(5, 2), default=18.00, nullable=False)
    
    # Overheads (editable)
    cc_pc = Column(Numeric(12, 2), default=20.00, nullable=False)
    vaince = Column(Numeric(12, 2), default=4.00, nullable=False)
    fda = Column(Numeric(12, 2), default=1.00, nullable=False)
    formulation_charge = Column(Numeric(12, 2), default=2.00, nullable=False)
    
    # Transport
    transport = Column(Numeric(12, 2), default=4.00, nullable=False)
    
    # Meta with indexes
    status = Column(String(16), default='draft', nullable=False, index=True)  # Filter by status
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=True, index=True)  # Filter by creator
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Sort by date
    notes = Column(Text, nullable=True)
    
    # Relationships
    created_by = relationship("User", back_populates="costings")
    packaging = relationship("PackagingOption", secondary="costing_packaging", back_populates="costings")
    costing_packaging = relationship("CostingPackaging", back_populates="costing", cascade="all, delete-orphan")
    
    # Composite indexes for common queries
    __table_args__ = (
        # Filter by status + sort by date
        Index('idx_costing_status_date', 'status', 'created_at'),
        # Search by project code + status
        Index('idx_costing_project_status', 'project_code', 'status'),
        # Filter by creator + date
        Index('idx_costing_creator_date', 'created_by_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Costing {self.product_name} ({self.project_code})>"


class CostingPackaging(Base):
    __tablename__ = "costing_packaging"
    
    id = Column(Integer, primary_key=True, index=True)
    costing_id = Column(Integer, ForeignKey('costing.id', ondelete='CASCADE'), nullable=False, index=True)
    packaging_id = Column(Integer, ForeignKey('packaging_option.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    
    # Relationships
    costing = relationship("Costing", back_populates="costing_packaging")
    packaging = relationship("PackagingOption")
    
    def __repr__(self):
        return f"<CostingPackaging {self.quantity}x>"