from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List
from decimal import Decimal
import io

from app.database import get_db
from app.models.quotation import Quotation, QuotationLine
from app.schemas.quotation import (
    QuotationCreate,
    QuotationUpdate,
    QuotationResponse,
)
from app.dependencies import get_current_active_user, CachedUser
from app.services.excel_export import generate_quotation_excel

router = APIRouter(prefix="/api", tags=["Quotations"])


@router.get("/quotations/", response_model=List[QuotationResponse])
async def quotation_list(
    skip: int = 0,
    limit: int = 100,
    project_code: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """List all quotations."""
    query = select(Quotation).options(selectinload(Quotation.lines))
    
    if project_code:
        query = query.where(Quotation.project_code == project_code)
    
    query = query.offset(skip).limit(limit).order_by(Quotation.created_at.desc())
    
    result = await db.execute(query)
    quotations = result.scalars().all()
    return quotations


@router.post("/quotations/", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def quotation_create(
    quotation_data: QuotationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Create new quotation with lines."""
    # Extract lines
    lines_data = quotation_data.lines
    quotation_dict = quotation_data.model_dump(exclude={'lines'})
    
    # Create quotation
    quotation = Quotation(**quotation_dict, created_by_id=current_user.id)
    db.add(quotation)
    await db.flush()
    
    # Add lines
    for line_data in lines_data:
        line_dict = line_data.model_dump()
        # Calculate line_total
        line_total = Decimal(line_data.unit_price) * Decimal(line_data.qty)
        line = QuotationLine(
            **line_dict,
            quotation_id=quotation.id,
            line_total=line_total
        )
        db.add(line)
    
    await db.commit()
    
    # Refresh with relationships
    result = await db.execute(
        select(Quotation)
        .where(Quotation.id == quotation.id)
        .options(selectinload(Quotation.lines))
    )
    quotation = result.scalar_one()
    return quotation


@router.get("/quotation/{project_code}/", response_model=QuotationResponse)
async def quotation_view(
    project_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """
    Get quotation by project code.
    CONVERTED FROM: Django views.quotation_view
    """
    result = await db.execute(
        select(Quotation)
        .where(Quotation.project_code == project_code)
        .options(selectinload(Quotation.lines))
        .order_by(Quotation.created_at.desc())
    )
    quotation = result.scalars().first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


@router.get("/quotation/{project_code}/export/")
async def export_quotation_excel(
    project_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """
    Export quotation to Excel.
    CONVERTED FROM: Django views.export_quotation_excel
    """
    result = await db.execute(
        select(Quotation)
        .where(Quotation.project_code == project_code)
        .options(selectinload(Quotation.lines))
        .order_by(Quotation.created_at.desc())
    )
    quotation = result.scalars().first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Generate Excel file
    excel_file = generate_quotation_excel(quotation)
    
    return StreamingResponse(
        io.BytesIO(excel_file),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=quotation_{project_code}.xlsx"}
    )


@router.delete("/quotations/{quotation_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def quotation_delete(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Delete a quotation."""
    result = await db.execute(select(Quotation).where(Quotation.id == quotation_id))
    quotation = result.scalar_one_or_none()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    await db.delete(quotation)
    await db.commit()
    return None
@router.put("/quotations/{quotation_id}/", response_model=QuotationResponse)
async def quotation_update(
    quotation_id: int,
    quotation_data: QuotationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Update an existing quotation."""
    result = await db.execute(
        select(Quotation)
        .where(Quotation.id == quotation_id)
        .options(selectinload(Quotation.lines))
    )
    quotation = result.scalar_one_or_none()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Update fields
    update_data = quotation_data.model_dump(exclude_unset=True, exclude={'lines'})
    for field, value in update_data.items():
        setattr(quotation, field, value)
    
    # Update lines if provided
    if quotation_data.lines is not None:
        # Bulk delete existing lines (single query instead of loop)
        await db.execute(
            delete(QuotationLine).where(QuotationLine.quotation_id == quotation_id)
        )
        
        # Add new lines
        for line_data in quotation_data.lines:
            line_dict = line_data.model_dump()
            line_total = Decimal(line_data.unit_price) * Decimal(line_data.qty)
            line = QuotationLine(
                **line_dict,
                quotation_id=quotation.id,
                line_total=line_total
            )
            db.add(line)
    
    await db.commit()
    
    # Refresh with relationships
    result = await db.execute(
        select(Quotation)
        .where(Quotation.id == quotation_id)
        .options(selectinload(Quotation.lines))
    )
    quotation = result.scalar_one()
    return quotation