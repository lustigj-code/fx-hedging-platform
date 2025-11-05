"""
ExchangeRate model - stores historical and current exchange rates.
"""
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_currency = Column(String(3), ForeignKey("currencies.code"), nullable=False, index=True)
    quote_currency = Column(String(3), ForeignKey("currencies.code"), nullable=False, index=True)
    rate = Column(DECIMAL(18, 8), nullable=False)  # Exchange rate with high precision
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # e.g., "exchangerate-api", "ECB", "Bloomberg"

    def __repr__(self):
        return f"<ExchangeRate {self.base_currency}/{self.quote_currency}: {self.rate} @ {self.timestamp}>"
