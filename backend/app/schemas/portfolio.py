"""
Pydantic schemas for portfolio analytics.
"""
from pydantic import BaseModel
from decimal import Decimal
from typing import List


class PortfolioExposure(BaseModel):
    """Exposure breakdown by currency pair."""

    currency_pair: str
    net_exposure: Decimal
    total_hedges: int
    total_premium_paid: Decimal
    average_strike: float
    total_notional: Decimal


class NettingOpportunity(BaseModel):
    """Potential netting between offsetting positions."""

    currency_pair: str
    long_exposure: Decimal
    short_exposure: Decimal
    netting_amount: Decimal
    potential_savings: Decimal


class PortfolioSummary(BaseModel):
    """Overall portfolio statistics."""

    total_transactions: int
    total_hedges: int
    total_premium_paid: Decimal
    total_notional_hedged: Decimal
    average_cost_percentage: float
    exposures_by_currency: List[PortfolioExposure]
    netting_opportunities: List[NettingOpportunity]
