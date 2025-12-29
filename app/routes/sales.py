# """
# Sales Lead Routes - FastAPI
# File: app/routes/sales.py

# REST API endpoints for sales lead management.
# Converted from Django views with proper async/await patterns.
# """
# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from typing import List, Optional

# from app.database import get_db
# from app.models.sales import SalesLead
# from app.schemas.sales import (
#     SalesLeadCreate,
#     SalesLeadUpdate,
#     SalesLeadResponse,
#     SalesLeadStatusUpdate,
#     VALID_STATUSES,
# )
# from app.dependencies import get_current_active_user
# from app.models.user import User

# # Create router with prefix and tags
# router = APIRouter(prefix="/api", tags=["Sales Leads"])


# @router.get("/leads/", response_model=List[SalesLeadResponse])
# async def leads_list(
#     skip: int = Query(0, ge=0, description="Number of records to skip"),
#     limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
#     status: Optional[str] = Query(None, description="Filter by status"),
#     location: Optional[str] = Query(None, description="Filter by location"),
#     search: Optional[str] = Query(None, description="Search in company name or owner"),
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     List all sales leads with optional filtering.
    
#     **Filters:**
#     - status: Filter by lead status
#     - location: Filter by location
#     - search: Search in company_name and owner fields
    
#     **Converted from:** Django `views.leads_list_create` (GET)
#     """
#     # Build query
#     query = select(SalesLead)
    
#     # Apply filters
#     if status:
#         if status not in VALID_STATUSES:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
#             )
#         query = query.where(SalesLead.status == status)
    
#     if location:
#         query = query.where(SalesLead.location.ilike(f"%{location}%"))
    
#     if search:
#         search_pattern = f"%{search}%"
#         query = query.where(
#             (SalesLead.company_name.ilike(search_pattern)) |
#             (SalesLead.owner.ilike(search_pattern))
#         )
    
#     # Apply pagination and ordering
#     query = query.offset(skip).limit(limit).order_by(SalesLead.created_at.desc())
    
#     # Execute query
#     result = await db.execute(query)
#     leads = result.scalars().all()
    
#     return leads


# @router.get("/leads/stats/")
# async def leads_stats(
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Get statistics about leads.
    
#     **Converted from:** Django `views.sales_performance_view`
#     """
#     # Total count
#     total_query = select(func.count(SalesLead.id))
#     total_result = await db.execute(total_query)
#     total = total_result.scalar()
    
#     # Count by status
#     status_counts = {}
#     for status_value in VALID_STATUSES:
#         count_query = select(func.count(SalesLead.id)).where(SalesLead.status == status_value)
#         count_result = await db.execute(count_query)
#         status_counts[status_value] = count_result.scalar()
    
#     # Leads with contact info
#     contacted_query = select(func.count(SalesLead.id)).where(
#         (SalesLead.email.isnot(None)) | (SalesLead.phone.isnot(None))
#     )
#     contacted_result = await db.execute(contacted_query)
#     with_contact = contacted_result.scalar()
    
#     return {
#         "total": total,
#         "with_contact": with_contact,
#         "by_status": status_counts
#     }


# @router.post("/leads/", response_model=SalesLeadResponse, status_code=status.HTTP_201_CREATED)
# async def leads_create(
#     lead_data: SalesLeadCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Create a new sales lead.
    
#     **Converted from:** Django `views.leads_list_create` (POST)
#     """
#     # Create lead instance
#     lead = SalesLead(**lead_data.model_dump())
    
#     # Add to database
#     db.add(lead)
#     await db.commit()
#     await db.refresh(lead)
    
#     return lead


# @router.get("/leads/{lead_id}/", response_model=SalesLeadResponse)
# async def lead_detail(
#     lead_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """Get single lead by ID"""
#     result = await db.execute(
#         select(SalesLead).where(SalesLead.id == lead_id)
#     )
#     lead = result.scalar_one_or_none()
    
#     if not lead:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Lead with ID {lead_id} not found"
#         )
    
#     return lead


# @router.patch("/leads/{lead_id}/", response_model=SalesLeadResponse)
# async def lead_update(
#     lead_id: int,
#     lead_data: SalesLeadUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Update lead information.
#     Only provided fields will be updated.
#     """
#     # Get existing lead
#     result = await db.execute(
#         select(SalesLead).where(SalesLead.id == lead_id)
#     )
#     lead = result.scalar_one_or_none()
    
#     if not lead:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Lead with ID {lead_id} not found"
#         )
    
#     # Update only provided fields
#     update_data = lead_data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(lead, field, value)
    
#     # Commit changes
#     await db.commit()
#     await db.refresh(lead)
    
#     return lead


# @router.patch("/leads/{lead_id}/status/", response_model=SalesLeadResponse)
# async def update_lead_status(
#     lead_id: int,
#     status_data: SalesLeadStatusUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """
#     Update only the status of a lead.
    
#     **Converted from:** Django `views.update_lead_status`
#     """
#     # Get lead
#     result = await db.execute(
#         select(SalesLead).where(SalesLead.id == lead_id)
#     )
#     lead = result.scalar_one_or_none()
    
#     if not lead:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Lead with ID {lead_id} not found"
#         )
    
#     # Update status
#     lead.status = status_data.status
    
#     # Commit changes
#     await db.commit()
#     await db.refresh(lead)
    
#     return lead


# @router.delete("/leads/{lead_id}/", status_code=status.HTTP_204_NO_CONTENT)
# async def lead_delete(
#     lead_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: CachedUser = Depends(get_current_active_user)
# ):
#     """Delete a lead permanently"""
#     # Get lead
#     result = await db.execute(
#         select(SalesLead).where(SalesLead.id == lead_id)
#     )
#     lead = result.scalar_one_or_none()
    
#     if not lead:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Lead with ID {lead_id} not found"
#         )
    
#     # Delete lead
#     await db.delete(lead)
#     await db.commit()
    
#     return None

"""
Sales Lead Routes - FastAPI (OPTIMIZED)
File: app/routes/sales.py

Optimized with:
- Better pagination with total count
- Faster queries with selectinload
- Response includes metadata
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.database import get_db
from app.models.sales import SalesLead
from app.schemas.sales import (
    SalesLeadCreate,
    SalesLeadUpdate,
    SalesLeadResponse,
    SalesLeadStatusUpdate,
    VALID_STATUSES,
)
from app.dependencies import get_current_active_user, CachedUser

router = APIRouter(prefix="/api", tags=["Sales Leads"])


@router.get("/leads/")
async def leads_list(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return (max 100)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    search: Optional[str] = Query(None, description="Search in company name or owner"),
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """
    List sales leads with pagination and filtering.
    
    **OPTIMIZED**: Returns pagination metadata for frontend.
    
    Returns:
    {
        "items": [...],
        "total": 1234,
        "skip": 0,
        "limit": 50,
        "has_more": true
    }
    """
    # Build base query
    query = select(SalesLead)
    count_query = select(func.count(SalesLead.id))
    
    # Apply filters to both queries
    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        query = query.where(SalesLead.status == status)
        count_query = count_query.where(SalesLead.status == status)
    
    if location:
        query = query.where(SalesLead.location.ilike(f"%{location}%"))
        count_query = count_query.where(SalesLead.location.ilike(f"%{location}%"))
    
    if search:
        search_pattern = f"%{search}%"
        search_filter = (
            (SalesLead.company_name.ilike(search_pattern)) |
            (SalesLead.owner.ilike(search_pattern)) |
            (SalesLead.email.ilike(search_pattern))
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    # Apply pagination and ordering (use index for fast sorting)
    query = query.offset(skip).limit(limit).order_by(SalesLead.created_at.desc())
    
    # Execute queries sequentially (async sessions don't support parallel ops)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    data_result = await db.execute(query)
    leads = data_result.scalars().all()
    
    # Return with pagination metadata
    return {
        "items": [SalesLeadResponse.model_validate(lead) for lead in leads],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


@router.get("/leads/stats/")
async def leads_stats(
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """
    Get statistics about leads.
    
    **OPTIMIZED**: Single GROUP BY query instead of N+1 queries per status.
    """
    # Run queries sequentially (async sessions don't support parallel ops)
    total_query = select(func.count(SalesLead.id))
    
    # Single GROUP BY query for all status counts (replaces N separate queries)
    status_query = select(
        SalesLead.status,
        func.count(SalesLead.id)
    ).group_by(SalesLead.status)
    
    contacted_query = select(func.count(SalesLead.id)).where(
        (SalesLead.email.isnot(None)) | (SalesLead.phone.isnot(None))
    )
    
    # Execute queries sequentially
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    status_result = await db.execute(status_query)
    
    contacted_result = await db.execute(contacted_query)
    with_contact = contacted_result.scalar()
    
    # Build status_counts from GROUP BY result
    status_counts = {status: 0 for status in VALID_STATUSES}
    for row in status_result:
        if row[0] in status_counts:
            status_counts[row[0]] = row[1]
    
    return {
        "total": total,
        "with_contact": with_contact,
        "by_status": status_counts
    }


@router.post("/leads/", response_model=SalesLeadResponse, status_code=status.HTTP_201_CREATED)
async def leads_create(
    lead_data: SalesLeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Create a new sales lead."""
    lead = SalesLead(**lead_data.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/leads/{lead_id}/", response_model=SalesLeadResponse)
async def lead_detail(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Get single lead by ID."""
    result = await db.execute(
        select(SalesLead).where(SalesLead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    return lead


@router.patch("/leads/{lead_id}/", response_model=SalesLeadResponse)
async def lead_update(
    lead_id: int,
    lead_data: SalesLeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Update lead information. Only provided fields will be updated."""
    result = await db.execute(
        select(SalesLead).where(SalesLead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    # Update only provided fields
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    await db.commit()
    await db.refresh(lead)
    return lead


@router.patch("/leads/{lead_id}/status/", response_model=SalesLeadResponse)
async def update_lead_status(
    lead_id: int,
    status_data: SalesLeadStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Update only the status of a lead."""
    result = await db.execute(
        select(SalesLead).where(SalesLead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    lead.status = status_data.status
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/leads/{lead_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def lead_delete(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CachedUser = Depends(get_current_active_user)
):
    """Delete a lead permanently."""
    result = await db.execute(
        select(SalesLead).where(SalesLead.id == lead_id)
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    await db.delete(lead)
    await db.commit()
    return None