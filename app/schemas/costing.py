from pydantic import BaseModel, ConfigDict, computed_field
from decimal import Decimal
from datetime import datetime


# PackagingOption Schemas
class PackagingOptionBase(BaseModel):
    name: str
    cost: Decimal = Decimal('0.00')


class PackagingOptionCreate(PackagingOptionBase):
    pass


class PackagingOptionResponse(PackagingOptionBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# CostingPackaging Schemas
class CostingPackagingBase(BaseModel):
    packaging_id: int
    quantity: int = 1


class CostingPackagingCreate(CostingPackagingBase):
    pass


class CostingPackagingResponse(BaseModel):
    id: int
    packaging_id: int
    quantity: int
    packaging: PackagingOptionResponse
    
    model_config = ConfigDict(from_attributes=True)


# Costing Schemas
class CostingBase(BaseModel):
    project_code: str
    product_name: str
    sku_ml: Decimal | None = None
    rm_per_litre: Decimal | None = None
    packaging_other: str | None = None
    packaging_cost_manual: Decimal | None = None
    batch_size_kg: Decimal = Decimal('500.00')
    gst_percent: Decimal = Decimal('18.00')
    cc_pc: Decimal = Decimal('20.00')
    vaince: Decimal = Decimal('4.00')
    fda: Decimal = Decimal('1.00')
    formulation_charge: Decimal = Decimal('2.00')
    transport: Decimal = Decimal('4.00')
    status: str = 'draft'
    notes: str | None = None


class CostingCreate(CostingBase):
    packaging_items: list[CostingPackagingCreate] = []


class CostingUpdate(BaseModel):
    project_code: str | None = None
    product_name: str | None = None
    sku_ml: Decimal | None = None
    rm_per_litre: Decimal | None = None
    packaging_other: str | None = None
    packaging_cost_manual: Decimal | None = None
    batch_size_kg: Decimal | None = None
    gst_percent: Decimal | None = None
    cc_pc: Decimal | None = None
    vaince: Decimal | None = None
    fda: Decimal | None = None
    formulation_charge: Decimal | None = None
    transport: Decimal | None = None
    status: str | None = None
    notes: str | None = None
    packaging_items: list[CostingPackagingCreate] | None = None


class CostingResponse(CostingBase):
    id: int
    created_at: datetime
    created_by_id: int | None
    costing_packaging: list[CostingPackagingResponse] = []
    
    # ============================================================
    # BUSINESS LOGIC FROM DJANGO MODELS - PRESERVED EXACTLY
    # ============================================================
    
    @computed_field
    @property
    def total_packaging_cost(self) -> Decimal:
        """
        Sum of packaging option costs * quantity + manual packaging cost (if any).
        EXACT LOGIC FROM DJANGO MODEL
        """
        total = Decimal('0.00')
        for cp in self.costing_packaging:
            qty = Decimal(cp.quantity or 1)
            total += (cp.packaging.cost or Decimal('0.00')) * qty
        if self.packaging_cost_manual:
            total += Decimal(self.packaging_cost_manual)
        return total.quantize(Decimal('0.01'))
    
    @computed_field
    @property
    def rm_cost_per_unit(self) -> Decimal:
        """
        RM cost per finished unit = rm_per_litre * (sku_ml / 1000)
        Returns 0 if values missing.
        EXACT LOGIC FROM DJANGO MODEL
        """
        try:
            if self.rm_per_litre is None or self.sku_ml is None:
                return Decimal('0.00')
            sku_l = Decimal(self.sku_ml) / Decimal('1000')
            return (Decimal(self.rm_per_litre) * sku_l).quantize(Decimal('0.01'))
        except Exception:
            return Decimal('0.00')
    
    @computed_field
    @property
    def unit_cost_before_gst(self) -> Decimal:
        """
        Sum of RM per unit + packaging + overheads (cc_pc, vaince, fda, formulation, transport)
        EXACT LOGIC FROM DJANGO MODEL
        """
        total = Decimal('0.00')
        total += self.rm_cost_per_unit
        total += self.total_packaging_cost
        total += Decimal(self.cc_pc or 0)
        total += Decimal(self.vaince or 0)
        total += Decimal(self.fda or 0)
        total += Decimal(self.formulation_charge or 0)
        total += Decimal(self.transport or 0)
        return total.quantize(Decimal('0.01'))
    
    @computed_field
    @property
    def gst_amount_per_unit(self) -> Decimal:
        """
        GST calculation
        EXACT LOGIC FROM DJANGO MODEL
        """
        try:
            gst = Decimal(self.gst_percent or 0) / Decimal('100')
            return (self.unit_cost_before_gst * gst).quantize(Decimal('0.01'))
        except Exception:
            return Decimal('0.00')
    
    @computed_field
    @property
    def final_unit_price(self) -> Decimal:
        """
        Final unit price with GST
        EXACT LOGIC FROM DJANGO MODEL
        """
        return (self.unit_cost_before_gst + self.gst_amount_per_unit).quantize(Decimal('0.01'))
    
    @computed_field
    @property
    def moq(self) -> int:
        """
        MOQ = batch_size_kg (converted to ml) / SKU (ml)
        i.e. batch_size_kg * 1000 / sku_ml
        If sku_ml missing or zero => 0
        EXACT LOGIC FROM DJANGO MODEL
        """
        try:
            if not self.sku_ml or Decimal(self.sku_ml) == 0:
                return 0
            batch_ml = Decimal(self.batch_size_kg) * Decimal('1000')
            moq_val = int((batch_ml // Decimal(self.sku_ml)))
            return moq_val
        except Exception:
            return 0
    
    model_config = ConfigDict(from_attributes=True)
