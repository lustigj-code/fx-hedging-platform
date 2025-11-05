"""
Application configuration and settings.
Manages environment variables and app-wide constants.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    APP_NAME: str = "FX Hedging Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./fx_hedging.db"
    # For production: "postgresql+asyncpg://user:password@localhost/dbname"

    # Exchange Rate API
    EXCHANGERATE_API_KEY: Optional[str] = None
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Open Exchange Rates (fallback)
    OPENEXCHANGERATES_API_KEY: Optional[str] = None
    OPENEXCHANGERATES_API_URL: str = "https://openexchangerates.org/api"

    # European Central Bank (for EUR pairs)
    ECB_API_URL: str = "https://www.ecb.europa.eu/stats/eurofxref"

    # Bloomberg (future integration)
    BLOOMBERG_API_KEY: Optional[str] = None

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://frontend-htjvjdcfu-lustigj-6781s-projects.vercel.app",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ]

    # Default parameters
    DEFAULT_PROTECTION_LEVEL: float = 0.05  # 5%
    DEFAULT_TIME_TO_MATURITY_DAYS: int = 90
    HISTORICAL_VOLATILITY_DAYS: int = 90
    MONTE_CARLO_SIMULATIONS: int = 10000

    # Risk-free rates (annual) - defaults
    DEFAULT_RISK_FREE_RATES: dict = {
        "USD": 0.0450,  # US 10Y Treasury
        "EUR": 0.0300,  # German 10Y Bund
        "GBP": 0.0420,  # UK 10Y Gilt
        "JPY": 0.0080,  # Japan 10Y JGB
        "MXN": 0.0900,  # Mexico 10Y
        "COP": 0.1100,  # Colombia 10Y
        "BRL": 0.1150,  # Brazil 10Y
        "CLP": 0.0580,  # Chile 10Y
        "PEN": 0.0650,  # Peru 10Y
        "ARS": 0.1800,  # Argentina (high risk)
        "UYU": 0.0850,  # Uruguay 10Y
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
