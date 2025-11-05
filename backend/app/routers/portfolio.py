"""
Portfolio analytics endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import PortfolioSummary, PortfolioExposure, NettingOpportunity

router = APIRouter()
portfolio_service = PortfolioService()


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive portfolio summary.

    Returns:
    - Total transactions and hedges
    - Total premium paid
    - Total notional hedged
    - Average cost percentage
    - Exposures by currency
    - Netting opportunities
    """
    summary = await portfolio_service.get_portfolio_summary(db)
    return summary


@router.get("/exposures", response_model=List[PortfolioExposure])
async def get_exposures(db: AsyncSession = Depends(get_db)):
    """
    Get portfolio exposures broken down by currency pair.

    Shows:
    - Net exposure (long/short)
    - Number of hedges
    - Total premium paid
    - Average strike price
    - Total notional amount
    """
    exposures = await portfolio_service.get_exposures_by_currency(db)
    return exposures


@router.get("/netting-opportunities", response_model=List[NettingOpportunity])
async def get_netting_opportunities(db: AsyncSession = Depends(get_db)):
    """
    Identify natural hedging opportunities.

    When a company has both imports (long) and exports (short) in the same
    currency pair, they can net these positions to reduce hedging costs.

    Returns opportunities with potential savings.
    """
    opportunities = await portfolio_service.find_netting_opportunities(db)
    return opportunities
