"""
Open Exchange Rates API data provider.
Free tier: 1,000 requests/month
https://openexchangerates.org/
"""
import httpx
from typing import Dict, List
from datetime import date, timedelta
from app.data_providers.base import ExchangeRateProvider
from app.config import settings


class OpenExchangeRatesProvider(ExchangeRateProvider):
    """Open Exchange Rates API provider (fallback option)."""

    def __init__(self):
        self.base_url = settings.OPENEXCHANGERATES_API_URL
        self.api_key = settings.OPENEXCHANGERATES_API_KEY

    async def get_current_rate(self, base: str, quote: str) -> float:
        """
        Get current exchange rate.

        API endpoint: /latest.json?app_id={api_key}&base={base}
        """
        if not self.api_key:
            raise ValueError("OPENEXCHANGERATES_API_KEY not configured")

        url = f"{self.base_url}/latest.json"
        params = {"app_id": self.api_key, "base": base}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if quote not in data.get("rates", {}):
                raise ValueError(f"Quote currency {quote} not found in response")

            return float(data["rates"][quote])

    async def get_historical_rates(
        self, base: str, quote: str, start_date: date, end_date: date
    ) -> List[Dict]:
        """
        Get historical rates.

        API endpoint: /historical/{date}.json?app_id={api_key}&base={base}

        Note: Historical rates require paid plan. Free tier only has latest.
        """
        if not self.api_key:
            raise ValueError("OPENEXCHANGERATES_API_KEY not configured")

        rates = []
        current_date = start_date

        async with httpx.AsyncClient(timeout=10.0) as client:
            while current_date <= end_date:
                url = f"{self.base_url}/historical/{current_date.strftime('%Y-%m-%d')}.json"
                params = {"app_id": self.api_key, "base": base}

                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()

                    if quote in data.get("rates", {}):
                        rates.append({"date": current_date, "rate": float(data["rates"][quote])})

                except Exception as e:
                    print(f"Error fetching rate for {current_date}: {e}")

                current_date += timedelta(days=1)

        return rates

    async def health_check(self) -> bool:
        """Check if API is accessible."""
        try:
            await self.get_current_rate("USD", "EUR")
            return True
        except Exception:
            return False
