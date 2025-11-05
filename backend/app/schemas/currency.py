"""
Pydantic schemas for Currency model.
"""
from pydantic import BaseModel, Field
from typing import Optional


class CurrencyBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    name: str = Field(..., min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    risk_free_rate: float = Field(..., ge=0, le=1, description="Annual risk-free rate")
    is_foreign: bool = True


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    risk_free_rate: Optional[float] = Field(None, ge=0, le=1)
    is_foreign: Optional[bool] = None


class CurrencyResponse(CurrencyBase):
    class Config:
        from_attributes = True
