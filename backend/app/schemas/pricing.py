"""
Pydantic schemas for pricing calculations.
"""
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional


class Greeks(BaseModel):
    """Option Greeks."""

    delta: float
    gamma: float
    vega: float
    theta: float


class ScenarioAnalysis(BaseModel):
    """Outcome at a specific future spot rate."""

    future_spot_rate: float
    unhedged_cost: float
    option_payoff: float
    net_cost: float
    savings_vs_unhedged: float


class PayoffCurvePoint(BaseModel):
    """Single point on the payoff diagram."""

    spot_rate: float
    unhedged_pnl: float
    option_payoff: float
    net_pnl: float


class PricingRequest(BaseModel):
    """Request to calculate option price."""

    spot_rate: float = Field(..., gt=0)
    strike_price: Optional[float] = None  # If None, calculated from protection_level
    time_to_maturity_years: float = Field(..., gt=0)
    volatility: float = Field(..., gt=0, le=2)  # Max 200% annualized
    domestic_rate: float = Field(..., ge=0, le=1)
    foreign_rate: float = Field(..., ge=0, le=1)
    notional_amount: float = Field(..., gt=0)
    option_type: str = Field(default="call", description="call or put")
    protection_level: float = Field(default=0.05, ge=0, le=0.20)  # 0% to 20%


class PricingResponse(BaseModel):
    """Response with calculated option price and analytics."""

    # Core pricing
    option_price_per_unit: float
    total_option_cost: float
    cost_percentage: float

    # Strike and protection
    strike_price: float
    protection_level: float
    max_cost_to_firm: float

    # Intermediate calculations
    d1: float
    d2: float

    # Greeks
    greeks: Greeks

    # Scenario analysis (5 scenarios: -10%, -5%, 0%, +5%, +10%)
    scenarios: list[ScenarioAnalysis]

    # Payoff curve data (for charting)
    payoff_curve: list[PayoffCurvePoint]

    # Break-even rate
    breakeven_rate: float
