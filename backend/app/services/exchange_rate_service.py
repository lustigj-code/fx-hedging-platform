"""
Exchange rate service - coordinates data providers and database storage.
"""
from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.exchange_rate import ExchangeRate
from app.data_providers.exchangerate_api import ExchangeRateAPIProvider
from app.config import settings


class ExchangeRateService:
    """Service for managing exchange rates."""

    def __init__(self):
        # Primary provider
        self.provider = ExchangeRateAPIProvider()

    async def get_current_rate(
        self, base: str, quote: str, db: AsyncSession, force_refresh: bool = False
    ) -> float:
        """
        Get current exchange rate, using cache if available.

        Args:
            base: Base currency code
            quote: Quote currency code
            db: Database session
            force_refresh: If True, fetch from API even if cached

        Returns:
            Exchange rate (quote per base)
        """
        # Check cache (rates from last 1 hour)
        if not force_refresh:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            stmt = (
                select(ExchangeRate)
                .where(
                    and_(
                        ExchangeRate.base_currency == base,
                        ExchangeRate.quote_currency == quote,
                        ExchangeRate.timestamp >= one_hour_ago,
                    )
                )
                .order_by(ExchangeRate.timestamp.desc())
                .limit(1)
            )

            result = await db.execute(stmt)
            cached_rate = result.scalar_one_or_none()

            if cached_rate:
                return float(cached_rate.rate)

        # Fetch from API
        rate = await self.provider.get_current_rate(base, quote)

        # Store in database
        db_rate = ExchangeRate(
            base_currency=base,
            quote_currency=quote,
            rate=rate,
            source="exchangerate-api",
            timestamp=datetime.utcnow(),
        )
        db.add(db_rate)
        await db.commit()

        return rate

    async def get_historical_rates(
        self, base: str, quote: str, start_date: date, end_date: date, db: AsyncSession
    ) -> List[dict]:
        """
        Get historical exchange rates for volatility calculation.

        First checks database, then fetches missing dates from API.

        Args:
            base: Base currency code
            quote: Quote currency code
            start_date: Start date
            end_date: End date
            db: Database session

        Returns:
            List of dicts with 'date' and 'rate'
        """
        # Query database for existing rates
        stmt = (
            select(ExchangeRate)
            .where(
                and_(
                    ExchangeRate.base_currency == base,
                    ExchangeRate.quote_currency == quote,
                    ExchangeRate.timestamp >= datetime.combine(start_date, datetime.min.time()),
                    ExchangeRate.timestamp <= datetime.combine(end_date, datetime.max.time()),
                )
            )
            .order_by(ExchangeRate.timestamp)
        )

        result = await db.execute(stmt)
        db_rates = result.scalars().all()

        # If we have enough data, return from cache
        if len(db_rates) >= (end_date - start_date).days * 0.8:  # 80% coverage
            return [{"date": r.timestamp.date(), "rate": float(r.rate)} for r in db_rates]

        # Otherwise, fetch from API
        api_rates = await self.provider.get_historical_rates(base, quote, start_date, end_date)

        # Store new rates in database
        for rate_data in api_rates:
            db_rate = ExchangeRate(
                base_currency=base,
                quote_currency=quote,
                rate=rate_data["rate"],
                source="exchangerate-api",
                timestamp=datetime.combine(rate_data["date"], datetime.min.time()),
            )
            db.add(db_rate)

        await db.commit()

        return api_rates

    async def refresh_rate(self, base: str, quote: str, db: AsyncSession) -> float:
        """Force refresh rate from API."""
        return await self.get_current_rate(base, quote, db, force_refresh=True)
