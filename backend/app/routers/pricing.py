"""
Pricing calculation endpoints.

This is the CORE of the platform - calculating FX option prices
using the Garman-Kohlhagen model.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.pricing import PricingRequest, PricingResponse
from app.services.pricing_engine import GarmanKohlhagenPricer
from app.services.exchange_rate_service import ExchangeRateService
from app.services.volatility_service import VolatilityService

router = APIRouter()
pricer = GarmanKohlhagenPricer()
exchange_rate_service = ExchangeRateService()
volatility_service = VolatilityService()


@router.post("/calculate", response_model=PricingResponse)
async def calculate_pricing(pricing_request: PricingRequest, db: AsyncSession = Depends(get_db)):
    """
    Calculate FX option price with full analytics.

    This endpoint:
    1. Takes spot rate, strike, volatility, rates, and notional
    2. Calculates option price using Garman-Kohlhagen formula
    3. Returns price, Greeks, scenarios, and payoff curve data

    This is THE MOST IMPORTANT endpoint for the investor demo.

    Example request body:
    {
        "spot_rate": 19.0,
        "time_to_maturity_years": 0.25,
        "volatility": 0.20,
        "domestic_rate": 0.04,
        "foreign_rate": 0.07,
        "notional_amount": 1000000,
        "option_type": "call",
        "protection_level": 0.05
    }

    Expected output for test case (S=19, K=19.95, T=0.25):
    - Option price per unit: ~0.343 MXN per USD
    - Total cost: ~343,000 MXN for $1M
    - Cost percentage: ~1.8% (well under 2% target!)
    """
    result = pricer.price_with_analytics(
        spot_rate=pricing_request.spot_rate,
        strike_price=pricing_request.strike_price,
        time_to_maturity_years=pricing_request.time_to_maturity_years,
        volatility=pricing_request.volatility,
        domestic_rate=pricing_request.domestic_rate,
        foreign_rate=pricing_request.foreign_rate,
        notional_amount=pricing_request.notional_amount,
        option_type=pricing_request.option_type,
        protection_level=pricing_request.protection_level,
    )

    return result


@router.post("/calculate-auto", response_model=PricingResponse)
async def calculate_pricing_auto(
    base: str,
    quote: str,
    time_to_maturity_years: float,
    notional_amount: float,
    option_type: str = "call",
    protection_level: float = 0.05,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate pricing with automatic data fetching.

    This endpoint automatically fetches:
    - Current spot rate from API
    - Historical volatility
    - Risk-free rates from currency table

    Makes it easy to get a quick quote without manually looking up market data.
    """
    from sqlalchemy import select
    from app.models.currency import Currency

    # Get current spot rate
    spot_rate = await exchange_rate_service.get_current_rate(base, quote, db)

    # Get volatility
    volatility = await volatility_service.get_or_default(base, quote, db, default=0.20)

    # Get risk-free rates
    base_currency_stmt = select(Currency).where(Currency.code == base.upper())
    base_currency_result = await db.execute(base_currency_stmt)
    base_currency = base_currency_result.scalar_one_or_none()

    quote_currency_stmt = select(Currency).where(Currency.code == quote.upper())
    quote_currency_result = await db.execute(quote_currency_stmt)
    quote_currency = quote_currency_result.scalar_one_or_none()

    if not base_currency or not quote_currency:
        raise HTTPException(
            status_code=400,
            detail="Currency not found. Please ensure currencies are seeded in the database."
        )

    foreign_rate = float(base_currency.risk_free_rate)
    domestic_rate = float(quote_currency.risk_free_rate)

    # Calculate strike
    strike_price = spot_rate * (1 + protection_level) if option_type == "call" else spot_rate * (1 - protection_level)

    # Price the option
    result = pricer.price_with_analytics(
        spot_rate=spot_rate,
        strike_price=strike_price,
        time_to_maturity_years=time_to_maturity_years,
        volatility=volatility,
        domestic_rate=domestic_rate,
        foreign_rate=foreign_rate,
        notional_amount=notional_amount,
        option_type=option_type,
        protection_level=protection_level,
    )

    return result
