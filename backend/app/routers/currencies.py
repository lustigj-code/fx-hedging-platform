"""
Currency management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyUpdate, CurrencyResponse

router = APIRouter()


@router.get("/", response_model=List[CurrencyResponse])
async def list_currencies(db: AsyncSession = Depends(get_db)):
    """Get all currencies."""
    stmt = select(Currency)
    result = await db.execute(stmt)
    currencies = result.scalars().all()
    return currencies


@router.get("/{code}", response_model=CurrencyResponse)
async def get_currency(code: str, db: AsyncSession = Depends(get_db)):
    """Get a specific currency by code."""
    stmt = select(Currency).where(Currency.code == code.upper())
    result = await db.execute(stmt)
    currency = result.scalar_one_or_none()

    if not currency:
        raise HTTPException(status_code=404, detail=f"Currency {code} not found")

    return currency


@router.post("/", response_model=CurrencyResponse, status_code=201)
async def create_currency(currency_data: CurrencyCreate, db: AsyncSession = Depends(get_db)):
    """Create a new currency."""
    # Check if currency already exists
    stmt = select(Currency).where(Currency.code == currency_data.code.upper())
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail=f"Currency {currency_data.code} already exists")

    currency = Currency(**currency_data.dict())
    currency.code = currency.code.upper()
    db.add(currency)
    await db.commit()
    await db.refresh(currency)

    return currency


@router.patch("/{code}", response_model=CurrencyResponse)
async def update_currency(code: str, currency_data: CurrencyUpdate, db: AsyncSession = Depends(get_db)):
    """Update a currency."""
    stmt = select(Currency).where(Currency.code == code.upper())
    result = await db.execute(stmt)
    currency = result.scalar_one_or_none()

    if not currency:
        raise HTTPException(status_code=404, detail=f"Currency {code} not found")

    update_data = currency_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(currency, field, value)

    await db.commit()
    await db.refresh(currency)

    return currency
