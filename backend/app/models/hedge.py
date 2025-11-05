"""
Hedge model - stores FX option hedge details.
"""
from sqlalchemy import Column, Integer, DECIMAL, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class HedgeStatus(enum.Enum):
    PROPOSED = "proposed"
    PURCHASED = "purchased"
    EXPIRED = "expired"
    EXERCISED = "exercised"


class Hedge(Base):
    __tablename__ = "hedges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)

    # Pricing parameters
    strike_price = Column(DECIMAL(18, 8), nullable=False)
    option_price_per_unit = Column(DECIMAL(18, 8), nullable=False)
    total_option_cost = Column(DECIMAL(18, 2), nullable=False)
    cost_percentage = Column(DECIMAL(5, 4), nullable=False)  # e.g., 0.0150 for 1.5%

    # Market parameters used in pricing
    volatility_used = Column(DECIMAL(8, 6), nullable=False)
    domestic_rate_used = Column(DECIMAL(6, 4), nullable=False)
    foreign_rate_used = Column(DECIMAL(6, 4), nullable=False)
    time_to_maturity_years = Column(DECIMAL(8, 6), nullable=False)
    protection_level = Column(DECIMAL(5, 4), nullable=False)  # e.g., 0.05 for 5%

    # Status and tracking
    status = Column(SQLEnum(HedgeStatus), nullable=False, default=HedgeStatus.PROPOSED)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<Hedge {self.id}: Transaction {self.transaction_id} @ K={self.strike_price} ({self.status.value})>"
