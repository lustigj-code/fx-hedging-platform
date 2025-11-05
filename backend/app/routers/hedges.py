"""
Hedge management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.hedge import Hedge, HedgeStatus
from app.schemas.hedge import HedgeCreate, HedgeUpdate, HedgeResponse

router = APIRouter()


@router.get("/", response_model=List[HedgeResponse])
async def list_hedges(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all hedges with optional status filter.

    Status options: proposed, purchased, expired, exercised
    """
    stmt = select(Hedge)

    if status:
        try:
            hedge_status = HedgeStatus(status.lower())
            stmt = stmt.where(Hedge.status == hedge_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    stmt = stmt.order_by(Hedge.created_at.desc())

    result = await db.execute(stmt)
    hedges = result.scalars().all()

    return hedges


@router.get("/{hedge_id}", response_model=HedgeResponse)
async def get_hedge(hedge_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific hedge by ID."""
    stmt = select(Hedge).where(Hedge.id == hedge_id)
    result = await db.execute(stmt)
    hedge = result.scalar_one_or_none()

    if not hedge:
        raise HTTPException(status_code=404, detail=f"Hedge {hedge_id} not found")

    return hedge


@router.post("/", response_model=HedgeResponse, status_code=201)
async def create_hedge(hedge_data: HedgeCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new hedge (purchase an option).

    This records the hedge in the database with all pricing parameters.
    In production, this would also trigger the actual trade execution.
    """
    hedge = Hedge(**hedge_data.dict())
    db.add(hedge)
    await db.commit()
    await db.refresh(hedge)

    # Update portfolio positions
    from app.services.portfolio_service import PortfolioService

    portfolio_service = PortfolioService()
    await portfolio_service.update_portfolio_positions(db)

    return hedge


@router.patch("/{hedge_id}/status", response_model=HedgeResponse)
async def update_hedge_status(hedge_id: int, hedge_update: HedgeUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update hedge status.

    Status transitions:
    - proposed -> purchased (when client confirms)
    - purchased -> expired (when option expires unexercised)
    - purchased -> exercised (when option is exercised)
    """
    stmt = select(Hedge).where(Hedge.id == hedge_id)
    result = await db.execute(stmt)
    hedge = result.scalar_one_or_none()

    if not hedge:
        raise HTTPException(status_code=404, detail=f"Hedge {hedge_id} not found")

    if hedge_update.status:
        try:
            new_status = HedgeStatus(hedge_update.status.lower())
            hedge.status = new_status
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {hedge_update.status}")

    await db.commit()
    await db.refresh(hedge)

    return hedge
