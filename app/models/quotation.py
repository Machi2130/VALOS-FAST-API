# from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from app.database import Base


# class Quotation(Base):
#     __tablename__ = "quotation"
    
#     id = Column(Integer, primary_key=True, index=True)
#     project_code = Column(String(16), index=True, nullable=False)
#     created_by_id = Column(Integer, ForeignKey('user.id'), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     notes = Column(Text, nullable=True)
#     exported_file = Column(String(500), nullable=True)
    
#     # Relationships
#     created_by = relationship("User", back_populates="quotations")
#     lines = relationship("QuotationLine", back_populates="quotation", cascade="all, delete-orphan")
    
#     def __repr__(self):
#         return f"<Quotation {self.project_code}>"


# class QuotationLine(Base):
#     __tablename__ = "quotation_line"
    
#     id = Column(Integer, primary_key=True, index=True)
#     quotation_id = Column(Integer, ForeignKey('quotation.id', ondelete='CASCADE'), nullable=False)
#     costing_id = Column(Integer, ForeignKey('costing.id', ondelete='SET NULL'), nullable=True)
    
#     product_name = Column(String(255), nullable=False)
#     unit_price = Column(Numeric(14, 2), nullable=False)
#     qty = Column(Integer, default=1, nullable=False)
#     line_total = Column(Numeric(16, 2), nullable=False)
    
#     # Relationships
#     quotation = relationship("Quotation", back_populates="lines")
#     costing = relationship("Costing")
    
#     def __repr__(self):
#         return f"<QuotationLine {self.product_name}>"

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Quotation(Base):
    __tablename__ = "quotation"
    
    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(16), index=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    exported_file = Column(String(500), nullable=True)
    
    # Relationships
    created_by = relationship("User", back_populates="quotations")
    lines = relationship("QuotationLine", back_populates="quotation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quotation {self.project_code}>"


class QuotationLine(Base):
    __tablename__ = "quotation_line"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id', ondelete='CASCADE'), nullable=False)
    costing_id = Column(Integer, ForeignKey('costing.id', ondelete='SET NULL'), nullable=True)
    
    product_name = Column(String(255), nullable=False)
    unit_price = Column(Numeric(14, 2), nullable=False)
    qty = Column(Integer, default=1, nullable=False)
    line_total = Column(Numeric(16, 2), nullable=False)
    
    # Relationships
    quotation = relationship("Quotation", back_populates="lines")
    costing = relationship("Costing")
    
    def __repr__(self):
        return f"<QuotationLine {self.product_name}>"