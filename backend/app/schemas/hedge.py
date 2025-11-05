"""
Pydantic schemas for Hedge model.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class HedgeBase(BaseModel):
    transaction_id: int
    strike_price: Decimal
    option_price_per_unit: Decimal
    total_option_cost: Decimal
    cost_percentage: Decimal
    volatility_used: Decimal
    domestic_rate_used: Decimal
    foreign_rate_used: Decimal
    time_to_maturity_years: Decimal
    protection_level: Decimal = Field(default=Decimal("0.05"))


class HedgeCreate(HedgeBase):
    pass


class HedgeUpdate(BaseModel):
    status: Optional[str] = None


class HedgeResponse(HedgeBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
