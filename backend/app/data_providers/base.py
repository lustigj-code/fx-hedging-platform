"""
Base interface for exchange rate data providers.
This allows easy switching between different data sources.
"""
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import date


class ExchangeRateProvider(ABC):
    """Abstract base class for exchange rate data providers."""

    @abstractmethod
    async def get_current_rate(self, base: str, quote: str) -> float:
        """
        Get current exchange rate for a currency pair.

        Args:
            base: Base currency code (e.g., "USD")
            quote: Quote currency code (e.g., "MXN")

        Returns:
            Exchange rate (quote per base)
        """
        pass

    @abstractmethod
    async def get_historical_rates(
        self, base: str, quote: str, start_date: date, end_date: date
    ) -> List[Dict]:
        """
        Get historical exchange rates for a date range.

        Args:
            base: Base currency code
            quote: Quote currency code
            start_date: Start date
            end_date: End date

        Returns:
            List of dicts with 'date' and 'rate' keys
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the data provider is accessible.

        Returns:
            True if healthy, False otherwise
        """
        pass
