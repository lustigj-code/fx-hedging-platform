"""
Exchange rate endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import get_db
from app.services.exchange_rate_service import ExchangeRateService

router = APIRouter()
exchange_rate_service = ExchangeRateService()


@router.get("/current")
async def get_current_rate(
    base: str = Query(..., description="Base currency code"),
    quote: str = Query(..., description="Quote currency code"),
    force_refresh: bool = Query(False, description="Force refresh from API"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current exchange rate for a currency pair.

    Returns the latest rate, fetching from API if not cached or if force_refresh=True.
    """
    rate = await exchange_rate_service.get_current_rate(base, quote, db, force_refresh)

    return {
        "base_currency": base,
        "quote_currency": quote,
        "rate": rate,
        "description": f"1 {base} = {rate} {quote}",
    }


@router.get("/historical")
async def get_historical_rates(
    base: str = Query(..., description="Base currency code"),
    quote: str = Query(..., description="Quote currency code"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get historical exchange rates for a date range.

    Used for volatility calculation and backtesting.
    """
    rates = await exchange_rate_service.get_historical_rates(base, quote, start_date, end_date, db)

    return {
        "base_currency": base,
        "quote_currency": quote,
        "start_date": start_date,
        "end_date": end_date,
        "count": len(rates),
        "rates": rates,
    }


@router.post("/refresh")
async def refresh_rate(
    base: str = Query(..., description="Base currency code"),
    quote: str = Query(..., description="Quote currency code"),
    db: AsyncSession = Depends(get_db),
):
    """Force refresh exchange rate from API."""
    rate = await exchange_rate_service.refresh_rate(base, quote, db)

    return {
        "base_currency": base,
        "quote_currency": quote,
        "rate": rate,
        "message": "Rate refreshed from API",
    }
