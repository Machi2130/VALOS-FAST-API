from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime


class QuotationLineBase(BaseModel):
    product_name: str
    unit_price: Decimal
    qty: int = 1
    costing_id: int | None = None


class QuotationLineCreate(QuotationLineBase):
    pass


class QuotationLineResponse(QuotationLineBase):
    id: int
    line_total: Decimal
    quotation_id: int
    
    model_config = ConfigDict(from_attributes=True)


class QuotationBase(BaseModel):
    project_code: str
    notes: str | None = None


class QuotationCreate(QuotationBase):
    lines: list[QuotationLineCreate] = []


class QuotationUpdate(BaseModel):
    notes: str | None = None
    lines: list[QuotationLineCreate] | None = None


class QuotationResponse(QuotationBase):
    id: int
    created_at: datetime
    created_by_id: int | None
    exported_file: str | None
    lines: list[QuotationLineResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
