"""
Volatility model - stores calculated volatility for currency pairs.
"""
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Volatility(Base):
    __tablename__ = "volatilities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    currency_pair = Column(String(7), nullable=False, index=True)  # e.g., "USDMXN"
    volatility = Column(DECIMAL(8, 6), nullable=False)  # Annualized volatility
    calculation_method = Column(String(50), nullable=False)  # e.g., "90-day historical"
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<Volatility {self.currency_pair}: {self.volatility} ({self.calculation_method})>"
