"""
Transaction model - stores foreign currency transactions.
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class TransactionType(enum.Enum):
    IMPORT = "import"  # Fear foreign currency appreciation
    EXPORT = "export"  # Fear foreign currency depreciation


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    invoice_date = Column(Date, nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    foreign_currency = Column(String(3), ForeignKey("currencies.code"), nullable=False, index=True)
    functional_currency = Column(String(3), ForeignKey("currencies.code"), nullable=False, index=True)
    notional_amount = Column(DECIMAL(18, 2), nullable=False)  # Amount in foreign currency
    spot_rate_at_invoice = Column(DECIMAL(18, 8), nullable=True)  # Rate when invoice created
    invoice_reference = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    source = Column(String(50), nullable=False, default="manual")  # manual, odoo, api, demo
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id}: {self.transaction_type.value} {self.notional_amount} {self.foreign_currency}>"
