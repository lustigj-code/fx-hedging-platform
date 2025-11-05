"""
Currency model - stores currency metadata and risk-free rates.
"""
from sqlalchemy import Column, String, Boolean, DECIMAL
from app.database import Base


class Currency(Base):
    __tablename__ = "currencies"

    code = Column(String(3), primary_key=True, index=True)  # ISO 4217 code
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=True)
    risk_free_rate = Column(DECIMAL(6, 4), nullable=False)  # Annual rate, e.g., 0.0450 for 4.5%
    is_foreign = Column(Boolean, default=True)  # For classification purposes

    def __repr__(self):
        return f"<Currency {self.code}: {self.name}>"
