"""
Demo data generator service.

Creates realistic sample transactions for Latin American businesses.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
import random
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction, TransactionType
from app.models.currency import Currency
from app.models.exchange_rate import ExchangeRate


class DemoService:
    """Service for generating demo data."""

    # Realistic scenarios for Latin America
    DEMO_SCENARIOS = [
        {
            "type": TransactionType.IMPORT,
            "foreign_currency": "USD",
            "functional_currency": "MXN",
            "notional": 1000000,
            "days_until_payment": 90,
            "description": "Machinery import from USA",
            "invoice_ref": "INV-MEX-001",
        },
        {
            "type": TransactionType.EXPORT,
            "foreign_currency": "USD",
            "functional_currency": "COP",
            "notional": 500000,
            "days_until_payment": 60,
            "description": "Coffee export to USA",
            "invoice_ref": "EXP-COL-001",
        },
        {
            "type": TransactionType.IMPORT,
            "foreign_currency": "EUR",
            "functional_currency": "BRL",
            "notional": 750000,
            "days_until_payment": 120,
            "description": "Auto parts import from Germany",
            "invoice_ref": "INV-BRA-001",
        },
        {
            "type": TransactionType.IMPORT,
            "foreign_currency": "USD",
            "functional_currency": "CLP",
            "notional": 300000,
            "days_until_payment": 45,
            "description": "Electronics import from China",
            "invoice_ref": "INV-CHI-001",
        },
        {
            "type": TransactionType.EXPORT,
            "foreign_currency": "EUR",
            "functional_currency": "ARS",
            "notional": 200000,
            "days_until_payment": 90,
            "description": "Wine export to Europe",
            "invoice_ref": "EXP-ARG-001",
        },
        {
            "type": TransactionType.IMPORT,
            "foreign_currency": "USD",
            "functional_currency": "PEN",
            "notional": 400000,
            "days_until_payment": 75,
            "description": "Medical equipment import",
            "invoice_ref": "INV-PER-001",
        },
        {
            "type": TransactionType.EXPORT,
            "foreign_currency": "USD",
            "functional_currency": "UYU",
            "notional": 350000,
            "days_until_payment": 60,
            "description": "Beef export to USA",
            "invoice_ref": "EXP-URU-001",
        },
        {
            "type": TransactionType.IMPORT,
            "foreign_currency": "GBP",
            "functional_currency": "MXN",
            "notional": 250000,
            "days_until_payment": 90,
            "description": "Industrial equipment from UK",
            "invoice_ref": "INV-MEX-002",
        },
    ]

    async def generate_demo_transactions(
        self, db: AsyncSession, num_transactions: int = None
    ) -> List[Transaction]:
        """
        Generate demo transactions.

        Args:
            db: Database session
            num_transactions: Number of transactions to generate (None = use all scenarios)

        Returns:
            List of created Transaction objects
        """
        if num_transactions is None:
            scenarios = self.DEMO_SCENARIOS
        else:
            scenarios = random.sample(self.DEMO_SCENARIOS, min(num_transactions, len(self.DEMO_SCENARIOS)))

        transactions = []
        today = date.today()

        for scenario in scenarios:
            invoice_date = today - timedelta(days=random.randint(0, 30))  # Within last month
            payment_date = invoice_date + timedelta(days=scenario["days_until_payment"])

            transaction = Transaction(
                transaction_type=scenario["type"],
                invoice_date=invoice_date,
                payment_date=payment_date,
                foreign_currency=scenario["foreign_currency"],
                functional_currency=scenario["functional_currency"],
                notional_amount=Decimal(str(scenario["notional"])),
                invoice_reference=scenario["invoice_ref"],
                description=scenario["description"],
                source="demo",
            )

            db.add(transaction)
            transactions.append(transaction)

        await db.commit()

        return transactions

    async def seed_currencies(self, db: AsyncSession) -> List[Currency]:
        """
        Seed the database with common currencies and their risk-free rates.

        Args:
            db: Database session

        Returns:
            List of created Currency objects
        """
        currencies_data = [
            {"code": "USD", "name": "US Dollar", "symbol": "$", "risk_free_rate": 0.0450},
            {"code": "EUR", "name": "Euro", "symbol": "€", "risk_free_rate": 0.0300},
            {"code": "GBP", "name": "British Pound", "symbol": "£", "risk_free_rate": 0.0420},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "risk_free_rate": 0.0080},
            {"code": "MXN", "name": "Mexican Peso", "symbol": "$", "risk_free_rate": 0.0900},
            {"code": "COP", "name": "Colombian Peso", "symbol": "$", "risk_free_rate": 0.1100},
            {"code": "BRL", "name": "Brazilian Real", "symbol": "R$", "risk_free_rate": 0.1150},
            {"code": "CLP", "name": "Chilean Peso", "symbol": "$", "risk_free_rate": 0.0580},
            {"code": "PEN", "name": "Peruvian Sol", "symbol": "S/", "risk_free_rate": 0.0650},
            {"code": "ARS", "name": "Argentine Peso", "symbol": "$", "risk_free_rate": 0.1800},
            {"code": "UYU", "name": "Uruguayan Peso", "symbol": "$", "risk_free_rate": 0.0850},
            {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "risk_free_rate": 0.0280},
        ]

        currencies = []

        for curr_data in currencies_data:
            # Check if currency already exists
            from sqlalchemy import select

            stmt = select(Currency).where(Currency.code == curr_data["code"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                currency = Currency(**curr_data)
                db.add(currency)
                currencies.append(currency)

        await db.commit()

        return currencies

    async def seed_demo_exchange_rates(self, db: AsyncSession) -> List[ExchangeRate]:
        """
        Seed the database with hardcoded exchange rates for demo purposes.

        This avoids calling external APIs during demo generation.
        Uses realistic exchange rates as of typical market conditions.

        Args:
            db: Database session

        Returns:
            List of created ExchangeRate objects
        """
        from sqlalchemy import select

        # Hardcoded exchange rates for demo (avoiding external API calls)
        exchange_rates_data = [
            # USD to Latin American currencies
            {"base": "USD", "quote": "MXN", "rate": 19.0},
            {"base": "USD", "quote": "COP", "rate": 4100.0},
            {"base": "USD", "quote": "BRL", "rate": 5.0},
            {"base": "USD", "quote": "CLP", "rate": 900.0},
            {"base": "USD", "quote": "PEN", "rate": 3.75},
            {"base": "USD", "quote": "ARS", "rate": 350.0},
            {"base": "USD", "quote": "UYU", "rate": 39.0},
            # Major currency pairs
            {"base": "USD", "quote": "EUR", "rate": 0.92},
            {"base": "USD", "quote": "GBP", "rate": 0.79},
            {"base": "USD", "quote": "JPY", "rate": 150.0},
            {"base": "EUR", "quote": "USD", "rate": 1.087},
            {"base": "GBP", "quote": "USD", "rate": 1.266},
            # EUR to Latin American
            {"base": "EUR", "quote": "BRL", "rate": 5.43},
            {"base": "EUR", "quote": "ARS", "rate": 380.0},
            # GBP to Latin American
            {"base": "GBP", "quote": "MXN", "rate": 24.0},
            # Inverse pairs for common demo scenarios
            {"base": "MXN", "quote": "USD", "rate": 0.0526},
            {"base": "COP", "quote": "USD", "rate": 0.000244},
            {"base": "BRL", "quote": "EUR", "rate": 0.184},
            {"base": "CLP", "quote": "USD", "rate": 0.00111},
            {"base": "ARS", "quote": "EUR", "rate": 0.00263},
            {"base": "PEN", "quote": "USD", "rate": 0.267},
            {"base": "UYU", "quote": "USD", "rate": 0.0256},
        ]

        exchange_rates = []
        current_time = datetime.utcnow()

        for rate_data in exchange_rates_data:
            # Check if rate already exists (within last hour)
            one_hour_ago = current_time - timedelta(hours=1)
            stmt = select(ExchangeRate).where(
                ExchangeRate.base_currency == rate_data["base"],
                ExchangeRate.quote_currency == rate_data["quote"],
                ExchangeRate.timestamp >= one_hour_ago,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                exchange_rate = ExchangeRate(
                    base_currency=rate_data["base"],
                    quote_currency=rate_data["quote"],
                    rate=Decimal(str(rate_data["rate"])),
                    source="demo-hardcoded",
                    timestamp=current_time,
                )
                db.add(exchange_rate)
                exchange_rates.append(exchange_rate)

        await db.commit()

        return exchange_rates

    async def reset_demo_data(self, db: AsyncSession):
        """
        Clear all demo data from the database.

        Args:
            db: Database session
        """
        from sqlalchemy import delete
        from app.models.hedge import Hedge

        # Delete hedges first (foreign key constraint)
        await db.execute(delete(Hedge))

        # Delete demo transactions
        await db.execute(delete(Transaction).where(Transaction.source == "demo"))

        await db.commit()
