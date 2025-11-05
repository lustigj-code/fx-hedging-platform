"""
Pydantic schemas for Transaction model.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class TransactionBase(BaseModel):
    transaction_type: str = Field(..., description="import or export")
    invoice_date: date
    payment_date: date
    foreign_currency: str = Field(..., min_length=3, max_length=3)
    functional_currency: str = Field(..., min_length=3, max_length=3)
    notional_amount: Decimal = Field(..., gt=0, decimal_places=2)
    spot_rate_at_invoice: Optional[Decimal] = None
    invoice_reference: Optional[str] = None
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    source: str = "manual"


class TransactionUpdate(BaseModel):
    transaction_type: Optional[str] = None
    invoice_date: Optional[date] = None
    payment_date: Optional[date] = None
    notional_amount: Optional[Decimal] = None
    spot_rate_at_invoice: Optional[Decimal] = None
    invoice_reference: Optional[str] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionUpload(BaseModel):
    """Schema for bulk transaction upload."""

    transactions: list[TransactionCreate]
