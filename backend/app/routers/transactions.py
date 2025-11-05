"""
Transaction management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionUpload,
)

router = APIRouter()


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    transaction_type: Optional[str] = None,
    foreign_currency: Optional[str] = None,
    functional_currency: Optional[str] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all transactions with optional filters.

    Filters:
    - transaction_type: "import" or "export"
    - foreign_currency: Currency code (e.g., "USD")
    - functional_currency: Currency code (e.g., "MXN")
    - source: "manual", "odoo", "api", "demo"
    """
    stmt = select(Transaction)

    # Apply filters
    if transaction_type:
        try:
            txn_type = TransactionType(transaction_type.lower())
            stmt = stmt.where(Transaction.transaction_type == txn_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid transaction_type: {transaction_type}")

    if foreign_currency:
        stmt = stmt.where(Transaction.foreign_currency == foreign_currency.upper())

    if functional_currency:
        stmt = stmt.where(Transaction.functional_currency == functional_currency.upper())

    if source:
        stmt = stmt.where(Transaction.source == source.lower())

    stmt = stmt.order_by(Transaction.created_at.desc())

    result = await db.execute(stmt)
    transactions = result.scalars().all()

    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific transaction by ID."""
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    return transaction


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(transaction_data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new transaction.

    This is the main endpoint for users to input foreign currency transactions
    that need hedging.
    """
    # Validate transaction type
    try:
        txn_type = TransactionType(transaction_data.transaction_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid transaction_type: {transaction_data.transaction_type}"
        )

    transaction = Transaction(
        transaction_type=txn_type,
        invoice_date=transaction_data.invoice_date,
        payment_date=transaction_data.payment_date,
        foreign_currency=transaction_data.foreign_currency.upper(),
        functional_currency=transaction_data.functional_currency.upper(),
        notional_amount=transaction_data.notional_amount,
        spot_rate_at_invoice=transaction_data.spot_rate_at_invoice,
        invoice_reference=transaction_data.invoice_reference,
        description=transaction_data.description,
        source=transaction_data.source,
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int, transaction_data: TransactionUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a transaction."""
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    # Update fields
    update_data = transaction_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "transaction_type" and value:
            value = TransactionType(value.lower())
        setattr(transaction, field, value)

    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a transaction."""
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    await db.delete(transaction)
    await db.commit()

    return {"message": f"Transaction {transaction_id} deleted successfully"}


@router.post("/upload", response_model=List[TransactionResponse])
async def upload_transactions(upload_data: TransactionUpload, db: AsyncSession = Depends(get_db)):
    """
    Bulk upload transactions from CSV/JSON.

    This endpoint is for integrating with accounting software like Odoo.
    """
    created_transactions = []

    for txn_data in upload_data.transactions:
        try:
            txn_type = TransactionType(txn_data.transaction_type.lower())
        except ValueError:
            continue  # Skip invalid transactions

        transaction = Transaction(
            transaction_type=txn_type,
            invoice_date=txn_data.invoice_date,
            payment_date=txn_data.payment_date,
            foreign_currency=txn_data.foreign_currency.upper(),
            functional_currency=txn_data.functional_currency.upper(),
            notional_amount=txn_data.notional_amount,
            spot_rate_at_invoice=txn_data.spot_rate_at_invoice,
            invoice_reference=txn_data.invoice_reference,
            description=txn_data.description,
            source=txn_data.source,
        )

        db.add(transaction)
        created_transactions.append(transaction)

    await db.commit()

    # Refresh all
    for txn in created_transactions:
        await db.refresh(txn)

    return created_transactions
