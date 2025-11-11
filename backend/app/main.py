"""
FastAPI main application.

FX Hedging Platform - Corporate Foreign Exchange Risk Management System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db, close_db


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()

    # Auto-seed currencies on startup if database is empty
    from app.database import get_db
    from app.models.currency import Currency
    from sqlalchemy import select

    async for db in get_db():
        # Check if currencies exist
        result = await db.execute(select(Currency).limit(1))
        currencies = result.scalars().first()

        if not currencies:
            # Database is empty, seed currencies
            from app.routers.demo import seed_currencies_data
            print("🌱 Auto-seeding currencies on startup...")
            await seed_currencies_data(db)
            print("✅ Currencies seeded successfully")
        else:
            print(f"✅ Database already has currencies, skipping auto-seed")
        break

    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready FX hedging platform for SMEs using Garman-Kohlhagen option pricing",
    lifespan=lifespan,
)

# CORS middleware with dynamic origin checking for Vercel
def cors_origin_checker(origin: str) -> bool:
    """Check if origin is allowed (supports Vercel wildcard)."""
    if origin in settings.CORS_ORIGINS:
        return True
    # Allow all Vercel app deployments
    if origin.endswith(".vercel.app"):
        return True
    return False

# Get allowed origins
allowed_origins = settings.CORS_ORIGINS.copy()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "FX Hedging Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "operational",
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


# Import and include routers
from app.routers import (
    rates,
    volatility,
    transactions,
    pricing,
    hedges,
    portfolio,
    demo,
    currencies,
    integrations,
)

app.include_router(rates.router, prefix="/api/rates", tags=["Exchange Rates"])
app.include_router(volatility.router, prefix="/api/volatility", tags=["Volatility"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(pricing.router, prefix="/api/pricing", tags=["Pricing"])
app.include_router(hedges.router, prefix="/api/hedges", tags=["Hedges"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo"])
app.include_router(currencies.router, prefix="/api/currencies", tags=["Currencies"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
