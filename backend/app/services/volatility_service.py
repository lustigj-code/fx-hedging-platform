"""
Volatility calculation service.

Calculates historical volatility from exchange rate time series.
Uses log returns and annualizes with sqrt(252) trading days convention.
"""
from datetime import date, datetime, timedelta
from typing import Optional
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.volatility import Volatility
from app.services.exchange_rate_service import ExchangeRateService
from app.config import settings


class VolatilityService:
    """Service for calculating and managing volatility."""

    def __init__(self):
        self.exchange_rate_service = ExchangeRateService()

    async def calculate_historical_volatility(
        self,
        base: str,
        quote: str,
        db: AsyncSession,
        lookback_days: int = None,
        force_recalculate: bool = False,
    ) -> float:
        """
        Calculate annualized historical volatility from recent exchange rates.

        Method:
        1. Fetch historical rates for lookback period
        2. Calculate log returns: ln(S_t / S_{t-1})
        3. Calculate standard deviation of returns
        4. Annualize: σ_annual = σ_daily * √252

        Args:
            base: Base currency code
            quote: Quote currency code
            db: Database session
            lookback_days: Number of days to look back (default: 90)
            force_recalculate: If True, recalculate even if cached

        Returns:
            Annualized volatility (e.g., 0.20 for 20%)
        """
        if lookback_days is None:
            lookback_days = settings.HISTORICAL_VOLATILITY_DAYS

        currency_pair = f"{base}{quote}"

        # Check cache (volatilities calculated in last 24 hours)
        if not force_recalculate:
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            stmt = (
                select(Volatility)
                .where(
                    and_(
                        Volatility.currency_pair == currency_pair,
                        Volatility.calculated_at >= one_day_ago,
                    )
                )
                .order_by(Volatility.calculated_at.desc())
                .limit(1)
            )

            result = await db.execute(stmt)
            cached_vol = result.scalar_one_or_none()

            if cached_vol:
                return float(cached_vol.volatility)

        # Fetch historical rates
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days + 10)  # Buffer for missing data

        rates = await self.exchange_rate_service.get_historical_rates(base, quote, start_date, end_date, db)

        if len(rates) < 30:  # Minimum data points
            raise ValueError(f"Insufficient data for volatility calculation: only {len(rates)} days")

        # Convert to pandas DataFrame for easier calculation
        df = pd.DataFrame(rates)
        df = df.sort_values("date")

        # Calculate log returns
        df["log_return"] = np.log(df["rate"] / df["rate"].shift(1))

        # Drop NaN values
        returns = df["log_return"].dropna()

        # Calculate daily volatility (standard deviation of log returns)
        daily_volatility = returns.std()

        # Annualize using sqrt(252) convention (252 trading days per year)
        annualized_volatility = daily_volatility * np.sqrt(252)

        # Store in database
        db_vol = Volatility(
            currency_pair=currency_pair,
            volatility=float(annualized_volatility),
            calculation_method=f"{lookback_days}-day historical",
            calculated_at=datetime.utcnow(),
        )
        db.add(db_vol)
        await db.commit()

        return float(annualized_volatility)

    async def get_volatility(
        self, base: str, quote: str, db: AsyncSession, force_recalculate: bool = False
    ) -> float:
        """
        Get volatility for a currency pair.

        This is the main public method.
        """
        return await self.calculate_historical_volatility(
            base, quote, db, force_recalculate=force_recalculate
        )

    async def get_or_default(self, base: str, quote: str, db: AsyncSession, default: float = 0.20) -> float:
        """
        Get volatility or return default if calculation fails.

        Args:
            base: Base currency code
            quote: Quote currency code
            db: Database session
            default: Default volatility if calculation fails

        Returns:
            Calculated or default volatility
        """
        try:
            return await self.get_volatility(base, quote, db)
        except Exception as e:
            print(f"Volatility calculation failed: {e}. Using default {default}")
            return default
