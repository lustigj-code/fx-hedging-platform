"""
Volatility calculation endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.volatility_service import VolatilityService

router = APIRouter()
volatility_service = VolatilityService()


@router.get("/{currency_pair}")
async def get_volatility(
    currency_pair: str,
    force_recalculate: bool = Query(False, description="Force recalculation"),
    lookback_days: int = Query(90, description="Lookback period in days"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get annualized historical volatility for a currency pair.

    Currency pair format: "USDMXN" (base + quote)

    Returns:
        Annualized volatility (e.g., 0.20 for 20%)
    """
    # Parse currency pair
    if len(currency_pair) != 6:
        return {"error": "Currency pair must be 6 characters (e.g., USDMXN)"}

    base = currency_pair[:3].upper()
    quote = currency_pair[3:].upper()

    volatility = await volatility_service.calculate_historical_volatility(
        base, quote, db, lookback_days, force_recalculate
    )

    return {
        "currency_pair": currency_pair,
        "base_currency": base,
        "quote_currency": quote,
        "volatility": volatility,
        "volatility_percentage": volatility * 100,
        "lookback_days": lookback_days,
        "method": f"{lookback_days}-day historical",
    }


@router.post("/calculate")
async def calculate_volatility(
    base: str = Query(..., description="Base currency code"),
    quote: str = Query(..., description="Quote currency code"),
    lookback_days: int = Query(90, description="Lookback period in days"),
    db: AsyncSession = Depends(get_db),
):
    """Calculate and store volatility for a currency pair."""
    volatility = await volatility_service.calculate_historical_volatility(
        base, quote, db, lookback_days, force_recalculate=True
    )

    return {
        "currency_pair": f"{base}{quote}",
        "volatility": volatility,
        "volatility_percentage": volatility * 100,
        "message": "Volatility calculated and stored",
    }
