# """
# Costing Routes - FastAPI
# File: app/routes/costing.py

# Costing calculator endpoints with both JSON and FormData support.
# """
# from fastapi import APIRouter, Depends, HTTPException, status, Form
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload
# from typing import List, Optional
# from decimal import Decimal, InvalidOperation

# from app.database import get_db
# from app.models.costing import Costing, CostingPackaging, PackagingOption
# from app.schemas.costing import (
#     CostingCreate,
#     CostingUpdate,
#     CostingResponse,
#     PackagingOptionCreate,
#     PackagingOptionResponse,
# )
# from app.dependencies import get_current_active_user
# from app.models.user import User

# router = APIRouter(prefix="/api", tags=["Costing"])


# # ============================================
# # PACKAGING OPTIONS ENDPOINTS
# # ============================================

# @router.get("/packaging/", response_model=List[PackagingOptionResponse])
# async def packaging_list(
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     List all packaging options.
#     **Converted from:** Django `views.packaging_list`
#     """
#     result = await db.execute(
#         select(PackagingOption).order_by(PackagingOption.name)
#     )
#     packaging = result.scalars().all()
#     return packaging


# @router.post("/packaging/", response_model=PackagingOptionResponse, status_code=status.HTTP_201_CREATED)
# async def packaging_create(
#     packaging_data: PackagingOptionCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """Create new packaging option"""
#     # Check if name already exists
#     existing = await db.execute(
#         select(PackagingOption).where(PackagingOption.name == packaging_data.name)
#     )
#     if existing.scalar_one_or_none():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Packaging option '{packaging_data.name}' already exists"
#         )
    
#     packaging = PackagingOption(**packaging_data.model_dump())
#     db.add(packaging)
#     await db.commit()
#     await db.refresh(packaging)
#     return packaging


# # ============================================
# # COSTING ENDPOINTS - JSON VERSION
# # ============================================

# @router.get("/costings/", response_model=List[CostingResponse])
# async def costing_list_api(
#     skip: int = 0,
#     limit: int = 100,
#     project_code: Optional[str] = None,
#     status: Optional[str] = None,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     List all costings with optional filters.
#     **Converted from:** Django `views.costing_list_api`
#     """
#     query = select(Costing).options(
#         selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
#     )
    
#     if project_code:
#         query = query.where(Costing.project_code == project_code)
#     if status:
#         query = query.where(Costing.status == status)
    
#     query = query.offset(skip).limit(limit).order_by(Costing.created_at.desc())
    
#     result = await db.execute(query)
#     costings = result.scalars().all()
#     return costings


# @router.post("/costing/new/", response_model=CostingResponse, status_code=status.HTTP_201_CREATED)
# async def costing_new_json(
#     costing_data: CostingCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Create new costing (JSON version).
#     **Converted from:** Django `views.costing_new`
#     """
#     # Extract packaging items
#     packaging_items = costing_data.packaging_items
#     costing_dict = costing_data.model_dump(exclude={'packaging_items'})
    
#     # Create costing
#     costing = Costing(**costing_dict, created_by_id=current_user.id)
#     db.add(costing)
#     await db.flush()  # Get the ID
    
#     # Add packaging items
#     for item in packaging_items:
#         cp = CostingPackaging(
#             costing_id=costing.id,
#             packaging_id=item.packaging_id,
#             quantity=item.quantity
#         )
#         db.add(cp)
    
#     await db.commit()
    
#     # Refresh with relationships
#     result = await db.execute(
#         select(Costing)
#         .where(Costing.id == costing.id)
#         .options(
#             selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
#         )
#     )
#     costing = result.scalar_one()
#     return costing


# # ============================================
# # COSTING FORM DATA ENDPOINT (For Frontend)
# # ============================================

# def safe_decimal(value: Optional[str], default: Optional[Decimal] = None) -> Optional[Decimal]:
#     """
#     Safely convert string to Decimal.
#     Returns None for empty/invalid values.
#     """
#     if value is None or value == '' or value == 'null' or value == 'undefined':
#         return default
#     try:
#         return Decimal(str(value).strip())
#     except (InvalidOperation, ValueError):
#         return default


# @router.post("/costing/new/form/")
# async def costing_new_form(
#     # Required fields
#     project_code: str = Form(..., description="Unique project code"),
#     product_name: str = Form(..., description="Product name"),
    
#     # Optional numeric fields
#     sku_ml: Optional[str] = Form(None, description="SKU in ml"),
#     rm_per_litre: Optional[str] = Form(None, description="Raw material cost per litre"),
    
#     # Manual packaging
#     packaging_name: Optional[str] = Form(None, description="Manual packaging name"),
#     packaging_cost_manual: Optional[str] = Form(None, description="Manual packaging cost"),
    
#     # Batch and GST
#     batch_size_kg: Optional[str] = Form("500", description="Batch size in KG"),
#     gst_percent: Optional[str] = Form("18", description="GST percentage"),
    
#     # Overheads
#     cc_pc: Optional[str] = Form("12", description="CC/PC value"),
#     vaince: Optional[str] = Form("12", description="Vaince value"),
#     fda: Optional[str] = Form("1", description="FDA value"),
#     formulation_charge: Optional[str] = Form("2", description="Formulation charge"),
#     transport: Optional[str] = Form("4", description="Transport cost"),
    
#     # Optional text fields
#     notes: Optional[str] = Form(None, description="Additional notes"),
#     status: Optional[str] = Form("draft", description="Costing status"),
    
#     # Dependencies
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Create new costing from FormData (matches Django behavior).
    
#     This endpoint accepts form-data which is what your frontend sends.
#     **Converted from:** Django `views.costing_new`
#     """
#     try:
#         # Create costing with safe decimal conversion
#         costing = Costing(
#             project_code=project_code,
#             product_name=product_name,
#             sku_ml=safe_decimal(sku_ml),
#             rm_per_litre=safe_decimal(rm_per_litre),
#             packaging_other=packaging_name,
#             packaging_cost_manual=safe_decimal(packaging_cost_manual),
#             batch_size_kg=safe_decimal(batch_size_kg, Decimal("500")),
#             gst_percent=safe_decimal(gst_percent, Decimal("18")),
#             cc_pc=safe_decimal(cc_pc, Decimal("12")),
#             vaince=safe_decimal(vaince, Decimal("12")),
#             fda=safe_decimal(fda, Decimal("1")),
#             formulation_charge=safe_decimal(formulation_charge, Decimal("2")),
#             transport=safe_decimal(transport, Decimal("4")),
#             notes=notes if notes else None,
#             status=status if status else "draft",
#             created_by_id=current_user.id
#         )
        
#         db.add(costing)
#         await db.commit()
#         await db.refresh(costing)
        
#         return {
#             "success": True,
#             "id": costing.id,
#             "project_code": costing.project_code,
#             "message": "Costing created successfully"
#         }
        
#     except Exception as e:
#         await db.rollback()
#         # Log the actual error for debugging
#         import traceback
#         print(f"Error creating costing: {e}")
#         print(traceback.format_exc())
        
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail=f"Failed to create costing: {str(e)}"
#         )


# @router.get("/costing/{costing_id}/", response_model=CostingResponse)
# async def costing_detail(
#     costing_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """Get costing by ID with all calculations"""
#     result = await db.execute(
#         select(Costing)
#         .where(Costing.id == costing_id)
#         .options(
#             selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
#         )
#     )
#     costing = result.scalar_one_or_none()
    
#     if not costing:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Costing with ID {costing_id} not found"
#         )
    
#     return costing


# @router.put("/costing/{costing_id}/edit/", response_model=CostingResponse)
# async def costing_edit(
#     costing_id: int,
#     costing_data: CostingUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Edit existing costing.
#     **Converted from:** Django `views.costing_edit`
#     """
#     result = await db.execute(
#         select(Costing)
#         .where(Costing.id == costing_id)
#         .options(selectinload(Costing.costing_packaging))
#     )
#     costing = result.scalar_one_or_none()
    
#     if not costing:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Costing with ID {costing_id} not found"
#         )
    
#     # Update fields
#     update_data = costing_data.model_dump(exclude_unset=True, exclude={'packaging_items'})
#     for field, value in update_data.items():
#         setattr(costing, field, value)
    
#     # Update packaging if provided
#     if costing_data.packaging_items is not None:
#         # Delete existing packaging
#         existing = (await db.execute(
#             select(CostingPackaging).where(CostingPackaging.costing_id == costing_id)
#         )).scalars().all()
#         for cp in existing:
#             await db.delete(cp)
        
#         # Add new packaging
#         for item in costing_data.packaging_items:
#             cp = CostingPackaging(
#                 costing_id=costing.id,
#                 packaging_id=item.packaging_id,
#                 quantity=item.quantity
#             )
#             db.add(cp)
    
#     await db.commit()
    
#     # Refresh with relationships
#     result = await db.execute(
#         select(Costing)
#         .where(Costing.id == costing_id)
#         .options(
#             selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
#         )
#     )
#     costing = result.scalar_one()
#     return costing


# @router.post("/costing/{costing_id}/duplicate/", response_model=CostingResponse)
# async def costing_duplicate(
#     costing_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Duplicate existing costing.
#     **Converted from:** Django `views.costing_duplicate`
#     """
#     result = await db.execute(
#         select(Costing)
#         .where(Costing.id == costing_id)
#         .options(selectinload(Costing.costing_packaging))
#     )
#     original = result.scalar_one_or_none()
    
#     if not original:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Costing with ID {costing_id} not found"
#         )
    
#     # Create duplicate with modified name
#     duplicate = Costing(
#         project_code=f"{original.project_code}_copy",
#         product_name=f"{original.product_name} (Copy)",
#         sku_ml=original.sku_ml,
#         rm_per_litre=original.rm_per_litre,
#         packaging_other=original.packaging_other,
#         packaging_cost_manual=original.packaging_cost_manual,
#         batch_size_kg=original.batch_size_kg,
#         gst_percent=original.gst_percent,
#         cc_pc=original.cc_pc,
#         vaince=original.vaince,
#         fda=original.fda,
#         formulation_charge=original.formulation_charge,
#         transport=original.transport,
#         status='draft',
#         notes=original.notes,
#         created_by_id=current_user.id,
#     )
    
#     db.add(duplicate)
#     await db.flush()
    
#     # Copy packaging items
#     for cp in original.costing_packaging:
#         new_cp = CostingPackaging(
#             costing_id=duplicate.id,
#             packaging_id=cp.packaging_id,
#             quantity=cp.quantity
#         )
#         db.add(new_cp)
    
#     await db.commit()
    
#     # Refresh with relationships
#     result = await db.execute(
#         select(Costing)
#         .where(Costing.id == duplicate.id)
#         .options(
#             selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
#         )
#     )
#     duplicate = result.scalar_one()
#     return duplicate


# @router.delete("/costing/{costing_id}/")
# async def costing_delete(
#     costing_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """Delete a costing"""
#     result = await db.execute(
#         select(Costing).where(Costing.id == costing_id)
#     )
#     costing = result.scalar_one_or_none()
    
#     if not costing:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Costing with ID {costing_id} not found"
#         )
    
#     await db.delete(costing)
#     await db.commit()
    
#     return {"message": "Costing deleted successfully"}

"""
Costing Routes - FastAPI (OPTIMIZED)
File: app/routes/costing.py

Optimized with better pagination and query performance.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from decimal import Decimal, InvalidOperation

from app.database import get_db
from app.models.costing import Costing, CostingPackaging, PackagingOption
from app.schemas.costing import (
    CostingCreate,
    CostingUpdate,
    CostingResponse,
    PackagingOptionCreate,
    PackagingOptionResponse,
)
from app.dependencies import get_current_active_user, CachedUser

router = APIRouter(prefix="/api", tags=["Costing"])


# ============================================
# PACKAGING OPTIONS ENDPOINTS
# ============================================

@router.get("/packaging/", response_model=List[PackagingOptionResponse])
async def packaging_list(
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """
    List all packaging options.
    **OPTIMIZED**: Uses index on name for fast sorting.
    """
    result = await db.execute(
        select(PackagingOption).order_by(PackagingOption.name)
    )
    packaging = result.scalars().all()
    return packaging


@router.post("/packaging/", response_model=PackagingOptionResponse, status_code=status.HTTP_201_CREATED)
async def packaging_create(
    packaging_data: PackagingOptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Create new packaging option."""
    existing = await db.execute(
        select(PackagingOption).where(PackagingOption.name == packaging_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Packaging option '{packaging_data.name}' already exists"
        )
    
    packaging = PackagingOption(**packaging_data.model_dump())
    db.add(packaging)
    await db.commit()
    await db.refresh(packaging)
    return packaging


# ============================================
# COSTING ENDPOINTS - OPTIMIZED
# ============================================

@router.get("/costings/")
async def costing_list_api(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    project_code: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search in product name or project code"),
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """
    List costings with pagination and filtering.
    
    **OPTIMIZED**: Returns pagination metadata.
    
    Returns:
    {
        "items": [...],
        "total": 500,
        "skip": 0,
        "limit": 50,
        "has_more": true
    }
    """
    # Base query with optimized loading
    query = select(Costing).options(
        selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
    )
    count_query = select(func.count(Costing.id))
    
    # Apply filters
    if project_code:
        query = query.where(Costing.project_code == project_code)
        count_query = count_query.where(Costing.project_code == project_code)
    
    if status:
        query = query.where(Costing.status == status)
        count_query = count_query.where(Costing.status == status)
    
    if search:
        search_pattern = f"%{search}%"
        search_filter = (
            (Costing.product_name.ilike(search_pattern)) |
            (Costing.project_code.ilike(search_pattern))
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    # Apply pagination and ordering (uses index on created_at)
    query = query.offset(skip).limit(limit).order_by(Costing.created_at.desc())
    
    # Execute queries sequentially (async sessions don't support parallel ops)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    data_result = await db.execute(query)
    costings = data_result.scalars().all()
    
    return {
        "items": [CostingResponse.model_validate(c) for c in costings],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


def safe_decimal(value: Optional[str], default: Optional[Decimal] = None) -> Optional[Decimal]:
    """Safely convert string to Decimal."""
    if value is None or value == '' or value == 'null' or value == 'undefined':
        return default
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return default


@router.post("/costing/new/form/")
async def costing_new_form(
    project_code: str = Form(...),
    product_name: str = Form(...),
    sku_ml: Optional[str] = Form(None),
    rm_per_litre: Optional[str] = Form(None),
    packaging_name: Optional[str] = Form(None),
    packaging_cost_manual: Optional[str] = Form(None),
    batch_size_kg: Optional[str] = Form("500"),
    gst_percent: Optional[str] = Form("18"),
    cc_pc: Optional[str] = Form("12"),
    vaince: Optional[str] = Form("12"),
    fda: Optional[str] = Form("1"),
    formulation_charge: Optional[str] = Form("2"),
    transport: Optional[str] = Form("4"),
    notes: Optional[str] = Form(None),
    status: Optional[str] = Form("draft"),
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Create new costing from FormData."""
    try:
        costing = Costing(
            project_code=project_code,
            product_name=product_name,
            sku_ml=safe_decimal(sku_ml),
            rm_per_litre=safe_decimal(rm_per_litre),
            packaging_other=packaging_name,
            packaging_cost_manual=safe_decimal(packaging_cost_manual),
            batch_size_kg=safe_decimal(batch_size_kg, Decimal("500")),
            gst_percent=safe_decimal(gst_percent, Decimal("18")),
            cc_pc=safe_decimal(cc_pc, Decimal("12")),
            vaince=safe_decimal(vaince, Decimal("12")),
            fda=safe_decimal(fda, Decimal("1")),
            formulation_charge=safe_decimal(formulation_charge, Decimal("2")),
            transport=safe_decimal(transport, Decimal("4")),
            notes=notes if notes else None,
            status=status if status else "draft",
            created_by_id=current_user.id
        )
        
        db.add(costing)
        await db.commit()
        await db.refresh(costing)
        
        return {
            "success": True,
            "id": costing.id,
            "project_code": costing.project_code,
            "message": "Costing created successfully"
        }
        
    except Exception as e:
        await db.rollback()
        import traceback
        print(f"Error creating costing: {e}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to create costing: {str(e)}"
        )


@router.get("/costing/{costing_id}/", response_model=CostingResponse)
async def costing_detail(
    costing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Get costing by ID with all calculations."""
    result = await db.execute(
        select(Costing)
        .where(Costing.id == costing_id)
        .options(
            selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
        )
    )
    costing = result.scalar_one_or_none()
    
    if not costing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Costing with ID {costing_id} not found"
        )
    
    return costing


@router.put("/costing/{costing_id}/edit/", response_model=CostingResponse)
async def costing_edit(
    costing_id: int,
    costing_data: CostingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Edit existing costing."""
    result = await db.execute(
        select(Costing)
        .where(Costing.id == costing_id)
        .options(selectinload(Costing.costing_packaging))
    )
    costing = result.scalar_one_or_none()
    
    if not costing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Costing with ID {costing_id} not found"
        )
    
    # Update fields
    update_data = costing_data.model_dump(exclude_unset=True, exclude={'packaging_items'})
    for field, value in update_data.items():
        setattr(costing, field, value)
    
    # Update packaging if provided
    if costing_data.packaging_items is not None:
        # Bulk delete existing packaging (single query instead of loop)
        await db.execute(
            delete(CostingPackaging).where(CostingPackaging.costing_id == costing_id)
        )
        
        for item in costing_data.packaging_items:
            cp = CostingPackaging(
                costing_id=costing.id,
                packaging_id=item.packaging_id,
                quantity=item.quantity
            )
            db.add(cp)
    
    await db.commit()
    
    result = await db.execute(
        select(Costing)
        .where(Costing.id == costing_id)
        .options(
            selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
        )
    )
    costing = result.scalar_one()
    return costing


@router.post("/costing/{costing_id}/duplicate/", response_model=CostingResponse)
async def costing_duplicate(
    costing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Duplicate existing costing."""
    result = await db.execute(
        select(Costing)
        .where(Costing.id == costing_id)
        .options(selectinload(Costing.costing_packaging))
    )
    original = result.scalar_one_or_none()
    
    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Costing with ID {costing_id} not found"
        )
    
    duplicate = Costing(
        project_code=f"{original.project_code}_copy",
        product_name=f"{original.product_name} (Copy)",
        sku_ml=original.sku_ml,
        rm_per_litre=original.rm_per_litre,
        packaging_other=original.packaging_other,
        packaging_cost_manual=original.packaging_cost_manual,
        batch_size_kg=original.batch_size_kg,
        gst_percent=original.gst_percent,
        cc_pc=original.cc_pc,
        vaince=original.vaince,
        fda=original.fda,
        formulation_charge=original.formulation_charge,
        transport=original.transport,
        status='draft',
        notes=original.notes,
        created_by_id=current_user.id,
    )
    
    db.add(duplicate)
    await db.flush()
    
    for cp in original.costing_packaging:
        new_cp = CostingPackaging(
            costing_id=duplicate.id,
            packaging_id=cp.packaging_id,
            quantity=cp.quantity
        )
        db.add(new_cp)
    
    await db.commit()
    
    result = await db.execute(
        select(Costing)
        .where(Costing.id == duplicate.id)
        .options(
            selectinload(Costing.costing_packaging).selectinload(CostingPackaging.packaging)
        )
    )
    duplicate = result.scalar_one()
    return duplicate


@router.delete("/costing/{costing_id}/")
async def costing_delete(
    costing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Delete a costing."""
    result = await db.execute(
        select(Costing).where(Costing.id == costing_id)
    )
    costing = result.scalar_one_or_none()
    
    if not costing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Costing with ID {costing_id} not found"
        )
    
    await db.delete(costing)
    await db.commit()
    
    return {"message": "Costing deleted successfully"}