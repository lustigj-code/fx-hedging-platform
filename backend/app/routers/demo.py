"""
Demo data endpoints.

These endpoints allow easy demonstration of the platform to investors
with realistic Latin American business scenarios.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.services.demo_service import DemoService
from app.schemas.transaction import TransactionResponse
from app.schemas.currency import CurrencyResponse

router = APIRouter()
demo_service = DemoService()


@router.post("/generate", response_model=List[TransactionResponse])
async def generate_demo_data(num_transactions: int = None, db: AsyncSession = Depends(get_db)):
    """
    Generate realistic demo transactions for Latin American businesses.

    Scenarios include:
    - Mexican importer buying machinery from USA
    - Colombian coffee exporter to USA
    - Brazilian auto parts importer from Germany
    - Chilean electronics importer
    - Argentine wine exporter to Europe
    - Peruvian medical equipment importer
    - Uruguayan beef exporter to USA
    - Mexican industrial equipment importer from UK

    Args:
        num_transactions: Number of transactions to generate (default: all scenarios)

    Returns:
        List of created transactions
    """
    # Step 1: Seed currencies first (required for transactions and pricing)
    await demo_service.seed_currencies(db)

    # Step 2: Seed hardcoded exchange rates (avoids external API calls)
    await demo_service.seed_demo_exchange_rates(db)

    # Step 3: Generate demo transactions
    transactions = await demo_service.generate_demo_transactions(db, num_transactions)

    return transactions


@router.post("/seed-currencies", response_model=List[CurrencyResponse])
async def seed_currencies(db: AsyncSession = Depends(get_db)):
    """
    Seed the database with common currencies and their risk-free rates.

    Includes:
    - Major currencies: USD, EUR, GBP, JPY, CNY
    - Latin American: MXN, COP, BRL, CLP, PEN, ARS, UYU

    This should be run on first startup to populate the currency table.
    """
    currencies = await demo_service.seed_currencies(db)

    return currencies


@router.post("/reset")
async def reset_demo_data(db: AsyncSession = Depends(get_db)):
    """
    Clear all demo data from the database.

    This removes:
    - All demo transactions
    - All hedges associated with demo transactions

    Useful for resetting between investor demos.
    """
    await demo_service.reset_demo_data(db)

    return {
        "message": "Demo data cleared successfully",
        "note": "You can regenerate demo data using POST /api/demo/generate",
    }
