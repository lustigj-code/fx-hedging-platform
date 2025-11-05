"""
Portfolio analytics service.

Aggregates positions, calculates netting opportunities,
and provides portfolio-level risk metrics.
"""
from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.transaction import Transaction, TransactionType
from app.models.hedge import Hedge, HedgeStatus
from app.models.portfolio_position import PortfolioPosition
from app.schemas.portfolio import (
    PortfolioSummary,
    PortfolioExposure,
    NettingOpportunity,
)


class PortfolioService:
    """Service for portfolio analytics."""

    async def get_portfolio_summary(self, db: AsyncSession) -> PortfolioSummary:
        """
        Get comprehensive portfolio summary.

        Args:
            db: Database session

        Returns:
            PortfolioSummary with all analytics
        """
        # Count total transactions
        total_transactions_stmt = select(func.count(Transaction.id))
        total_transactions_result = await db.execute(total_transactions_stmt)
        total_transactions = total_transactions_result.scalar_one()

        # Count total hedges
        total_hedges_stmt = select(func.count(Hedge.id))
        total_hedges_result = await db.execute(total_hedges_stmt)
        total_hedges = total_hedges_result.scalar_one()

        # Sum total premium paid
        total_premium_stmt = select(func.sum(Hedge.total_option_cost)).where(
            Hedge.status.in_([HedgeStatus.PROPOSED, HedgeStatus.PURCHASED])
        )
        total_premium_result = await db.execute(total_premium_stmt)
        total_premium = total_premium_result.scalar_one() or Decimal("0")

        # Get exposures by currency
        exposures = await self.get_exposures_by_currency(db)

        # Calculate total notional hedged
        total_notional = sum(exp.total_notional for exp in exposures)

        # Calculate average cost percentage
        avg_cost_stmt = select(func.avg(Hedge.cost_percentage)).where(
            Hedge.status.in_([HedgeStatus.PROPOSED, HedgeStatus.PURCHASED])
        )
        avg_cost_result = await db.execute(avg_cost_stmt)
        avg_cost = avg_cost_result.scalar_one() or 0.0

        # Get netting opportunities
        netting_opportunities = await self.find_netting_opportunities(db)

        return PortfolioSummary(
            total_transactions=total_transactions,
            total_hedges=total_hedges,
            total_premium_paid=total_premium,
            total_notional_hedged=total_notional,
            average_cost_percentage=float(avg_cost) * 100,  # Convert to percentage
            exposures_by_currency=exposures,
            netting_opportunities=netting_opportunities,
        )

    async def get_exposures_by_currency(self, db: AsyncSession) -> List[PortfolioExposure]:
        """
        Get portfolio exposures broken down by currency pair.

        Args:
            db: Database session

        Returns:
            List of PortfolioExposure
        """
        # Query all transactions with their hedges
        transactions_stmt = select(Transaction)
        transactions_result = await db.execute(transactions_stmt)
        transactions = transactions_result.scalars().all()

        # Group by currency pair
        exposures_dict = {}

        for txn in transactions:
            currency_pair = f"{txn.foreign_currency}{txn.functional_currency}"

            if currency_pair not in exposures_dict:
                exposures_dict[currency_pair] = {
                    "net_exposure": Decimal("0"),
                    "notional_amount": Decimal("0"),
                    "hedge_count": 0,
                    "total_premium": Decimal("0"),
                    "total_strike_weighted": 0.0,
                    "total_notional_for_strike": Decimal("0"),
                }

            # Update exposure (imports are long foreign currency, exports are short)
            if txn.transaction_type == TransactionType.IMPORT:
                exposures_dict[currency_pair]["net_exposure"] += txn.notional_amount
            else:
                exposures_dict[currency_pair]["net_exposure"] -= txn.notional_amount

            exposures_dict[currency_pair]["notional_amount"] += txn.notional_amount

        # Get hedge data
        hedges_stmt = select(Hedge)
        hedges_result = await db.execute(hedges_stmt)
        hedges = hedges_result.scalars().all()

        # Join hedges with transactions to get currency pair
        for hedge in hedges:
            txn_stmt = select(Transaction).where(Transaction.id == hedge.transaction_id)
            txn_result = await db.execute(txn_stmt)
            txn = txn_result.scalar_one_or_none()

            if txn:
                currency_pair = f"{txn.foreign_currency}{txn.functional_currency}"
                if currency_pair in exposures_dict:
                    exposures_dict[currency_pair]["hedge_count"] += 1
                    exposures_dict[currency_pair]["total_premium"] += hedge.total_option_cost
                    exposures_dict[currency_pair]["total_strike_weighted"] += float(
                        hedge.strike_price * txn.notional_amount
                    )
                    exposures_dict[currency_pair]["total_notional_for_strike"] += txn.notional_amount

        # Convert to PortfolioExposure objects
        exposures = []
        for currency_pair, data in exposures_dict.items():
            # Calculate average strike
            if data["total_notional_for_strike"] > 0:
                avg_strike = data["total_strike_weighted"] / float(data["total_notional_for_strike"])
            else:
                avg_strike = 0.0

            exposures.append(
                PortfolioExposure(
                    currency_pair=currency_pair,
                    net_exposure=data["net_exposure"],
                    total_hedges=data["hedge_count"],
                    total_premium_paid=data["total_premium"],
                    average_strike=avg_strike,
                    total_notional=data["notional_amount"],
                )
            )

        return exposures

    async def find_netting_opportunities(self, db: AsyncSession) -> List[NettingOpportunity]:
        """
        Identify natural hedging opportunities.

        When a company has both imports (long) and exports (short) in the same
        currency pair, they can net these positions to reduce hedging costs.

        Args:
            db: Database session

        Returns:
            List of NettingOpportunity
        """
        # Query transactions grouped by currency pair and type
        transactions_stmt = select(Transaction)
        transactions_result = await db.execute(transactions_stmt)
        transactions = transactions_result.scalars().all()

        # Group by currency pair
        positions = {}

        for txn in transactions:
            currency_pair = f"{txn.foreign_currency}{txn.functional_currency}"

            if currency_pair not in positions:
                positions[currency_pair] = {"long": Decimal("0"), "short": Decimal("0")}

            if txn.transaction_type == TransactionType.IMPORT:
                positions[currency_pair]["long"] += txn.notional_amount
            else:
                positions[currency_pair]["short"] += txn.notional_amount

        # Find netting opportunities
        opportunities = []

        for currency_pair, pos in positions.items():
            if pos["long"] > 0 and pos["short"] > 0:
                netting_amount = min(pos["long"], pos["short"])

                # Estimate savings (assume 2% hedging cost on netted amount)
                potential_savings = netting_amount * Decimal("0.02")

                opportunities.append(
                    NettingOpportunity(
                        currency_pair=currency_pair,
                        long_exposure=pos["long"],
                        short_exposure=pos["short"],
                        netting_amount=netting_amount,
                        potential_savings=potential_savings,
                    )
                )

        return opportunities

    async def update_portfolio_positions(self, db: AsyncSession):
        """
        Update the portfolio_positions table with current aggregates.

        This can be called periodically or after each hedge creation.
        """
        exposures = await self.get_exposures_by_currency(db)

        for exp in exposures:
            # Check if position exists
            stmt = select(PortfolioPosition).where(PortfolioPosition.currency_pair == exp.currency_pair)
            result = await db.execute(stmt)
            position = result.scalar_one_or_none()

            if position:
                # Update existing
                position.net_exposure = exp.net_exposure
                position.total_hedges = exp.total_hedges
                position.total_premium_paid = exp.total_premium_paid
            else:
                # Create new
                position = PortfolioPosition(
                    currency_pair=exp.currency_pair,
                    net_exposure=exp.net_exposure,
                    total_hedges=exp.total_hedges,
                    total_premium_paid=exp.total_premium_paid,
                )
                db.add(position)

        await db.commit()
