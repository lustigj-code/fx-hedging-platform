"""
PortfolioPosition model - tracks aggregate positions by currency pair.
"""
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from sqlalchemy.sql import func
from app.database import Base


class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    currency_pair = Column(String(7), nullable=False, unique=True, index=True)  # e.g., "USDMXN"
    net_exposure = Column(DECIMAL(18, 2), nullable=False, default=0)  # Positive=long, Negative=short
    total_hedges = Column(Integer, nullable=False, default=0)
    total_premium_paid = Column(DECIMAL(18, 2), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<PortfolioPosition {self.currency_pair}: {self.net_exposure} ({self.total_hedges} hedges)>"
