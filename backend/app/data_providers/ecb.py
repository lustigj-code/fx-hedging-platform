"""
European Central Bank (ECB) data provider.
Free, no API key required
https://www.ecb.europa.eu/stats/eurofxref/
"""
import httpx
import xml.etree.ElementTree as ET
from typing import Dict, List
from datetime import date, timedelta, datetime
from app.data_providers.base import ExchangeRateProvider
from app.config import settings


class ECBProvider(ExchangeRateProvider):
    """
    European Central Bank provider.

    Free, reliable source for EUR exchange rates.
    Good for EUR pairs in Latin America (e.g., EUR/MXN, EUR/BRL).
    """

    def __init__(self):
        self.base_url = settings.ECB_API_URL
        self.daily_url = f"{self.base_url}/eurofxref-daily.xml"
        self.hist_90_url = f"{self.base_url}/eurofxref-hist-90d.xml"

    async def get_current_rate(self, base: str, quote: str) -> float:
        """
        Get current exchange rate.

        ECB only provides EUR as base. For other pairs, we calculate cross rates.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.daily_url)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)
            namespaces = {'ns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}

            # Get all rates for today
            rates = {}
            for cube in root.findall(".//ns:Cube[@currency]", namespaces):
                currency = cube.get('currency')
                rate = float(cube.get('rate'))
                rates[currency] = rate

            # Calculate rate
            if base == "EUR" and quote in rates:
                return rates[quote]
            elif quote == "EUR" and base in rates:
                return 1.0 / rates[base]
            elif base in rates and quote in rates:
                # Cross rate: EUR/BASE and EUR/QUOTE -> BASE/QUOTE
                return rates[quote] / rates[base]
            else:
                raise ValueError(f"Cannot calculate rate for {base}/{quote} using ECB data")

    async def get_historical_rates(
        self, base: str, quote: str, start_date: date, end_date: date
    ) -> List[Dict]:
        """
        Get historical rates (last 90 days available for free).

        For longer history, use paid services like Bloomberg.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.hist_90_url)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)
            namespaces = {'ns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}

            # Get all daily cubes
            rates_by_date = {}
            for time_cube in root.findall(".//ns:Cube[@time]", namespaces):
                date_str = time_cube.get('time')
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                if start_date <= date_obj <= end_date:
                    daily_rates = {}
                    for cube in time_cube.findall("ns:Cube[@currency]", namespaces):
                        currency = cube.get('currency')
                        rate = float(cube.get('rate'))
                        daily_rates[currency] = rate

                    rates_by_date[date_obj] = daily_rates

            # Calculate requested rate for each date
            result = []
            for date_obj, daily_rates in sorted(rates_by_date.items()):
                try:
                    if base == "EUR" and quote in daily_rates:
                        rate = daily_rates[quote]
                    elif quote == "EUR" and base in daily_rates:
                        rate = 1.0 / daily_rates[base]
                    elif base in daily_rates and quote in daily_rates:
                        rate = daily_rates[quote] / daily_rates[base]
                    else:
                        continue  # Skip if can't calculate

                    result.append({"date": date_obj, "rate": rate})

                except Exception:
                    continue

            return result

    async def health_check(self) -> bool:
        """Check if ECB API is accessible."""
        try:
            await self.get_current_rate("EUR", "USD")
            return True
        except Exception:
            return False
