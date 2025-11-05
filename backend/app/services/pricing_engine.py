"""
Garman-Kohlhagen FX Option Pricing Engine.

This module implements the exact Garman-Kohlhagen formula for pricing
European-style FX options. This is THE core of the platform.

Reference:
Garman, M.B. and Kohlhagen, S.W. (1983) "Foreign Currency Option Values"
Journal of International Money and Finance, 2, 231-237.
"""
from typing import Dict, List
import numpy as np
from decimal import Decimal
from app.utils.math_utils import cumulative_normal, probability_density_normal, generate_gbm_paths
from app.schemas.pricing import (
    PricingResponse,
    Greeks,
    ScenarioAnalysis,
    PayoffCurvePoint,
)


class GarmanKohlhagenPricer:
    """
    FX Option pricer using the Garman-Kohlhagen model.

    The model extends Black-Scholes to FX options by accounting for
    the foreign risk-free rate (treating foreign currency like a dividend-paying stock).
    """

    @staticmethod
    def calculate_call_option(
        spot_rate: float,
        strike_price: float,
        time_to_maturity_years: float,
        volatility: float,
        domestic_rate: float,
        foreign_rate: float,
    ) -> Dict:
        """
        Calculate FX call option price using Garman-Kohlhagen formula.

        A call option gives the right (but not obligation) to BUY foreign currency
        at the strike price. This protects an IMPORTER against appreciation.

        Formula:
        C = e^(-r_f * T) * S * N(d1) - K * e^(-r_d * T) * N(d2)

        where:
        d1 = [ln(S*e^(-r_f*T) / K*e^(-r_d*T))] / (sigma*sqrt(T)) + (sigma*sqrt(T))/2
        d2 = d1 - sigma*sqrt(T)

        Args:
            spot_rate: Current spot exchange rate (domestic per foreign, e.g., MXN per USD)
            strike_price: Strike price in same units as spot
            time_to_maturity_years: Time to maturity in years
            volatility: Annualized volatility (e.g., 0.20 for 20%)
            domestic_rate: Domestic risk-free rate (e.g., 0.04 for 4%)
            foreign_rate: Foreign risk-free rate (e.g., 0.07 for 7%)

        Returns:
            Dictionary with option_price, d1, d2, and greeks
        """
        # Handle edge case: expired option
        if time_to_maturity_years <= 0:
            intrinsic_value = max(0, spot_rate - strike_price)
            return {
                "option_price": intrinsic_value,
                "d1": 0,
                "d2": 0,
                "greeks": {"delta": 1 if spot_rate > strike_price else 0, "gamma": 0, "vega": 0, "theta": 0},
            }

        # Calculate d1 and d2 according to the exact formula
        sqrt_T = np.sqrt(time_to_maturity_years)
        vol_sqrt_T = volatility * sqrt_T

        # Forward rates with continuous compounding
        forward_spot = spot_rate * np.exp(-foreign_rate * time_to_maturity_years)
        forward_strike = strike_price * np.exp(-domestic_rate * time_to_maturity_years)

        # d1 calculation
        numerator = np.log(forward_spot / forward_strike)
        d1 = (numerator / vol_sqrt_T) + (vol_sqrt_T / 2)

        # d2 calculation
        d2 = d1 - vol_sqrt_T

        # Calculate option price
        N_d1 = cumulative_normal(d1)
        N_d2 = cumulative_normal(d2)

        discount_foreign = np.exp(-foreign_rate * time_to_maturity_years)
        discount_domestic = np.exp(-domestic_rate * time_to_maturity_years)

        term1 = discount_foreign * spot_rate * N_d1
        term2 = strike_price * discount_domestic * N_d2

        option_price = term1 - term2

        # Calculate Greeks
        delta = discount_foreign * N_d1

        pdf_d1 = probability_density_normal(d1)
        gamma = (discount_foreign * pdf_d1) / (spot_rate * vol_sqrt_T)

        vega = spot_rate * discount_foreign * pdf_d1 * sqrt_T

        theta_annual = (
            -(spot_rate * pdf_d1 * volatility * discount_foreign) / (2 * sqrt_T)
            + foreign_rate * spot_rate * N_d1 * discount_foreign
            - domestic_rate * strike_price * discount_domestic * N_d2
        )
        theta_daily = theta_annual / 365

        greeks = {
            "delta": float(delta),
            "gamma": float(gamma),
            "vega": float(vega / 100),  # Per 1% change in volatility
            "theta": float(theta_daily),
        }

        return {
            "option_price": float(option_price),
            "d1": float(d1),
            "d2": float(d2),
            "greeks": greeks,
        }

    @staticmethod
    def calculate_put_option(
        spot_rate: float,
        strike_price: float,
        time_to_maturity_years: float,
        volatility: float,
        domestic_rate: float,
        foreign_rate: float,
    ) -> Dict:
        """
        Calculate FX put option price using Garman-Kohlhagen formula.

        A put option gives the right to SELL foreign currency at the strike price.
        This protects an EXPORTER against depreciation.

        Formula:
        P = K * e^(-r_d * T) * N(-d2) - e^(-r_f * T) * S * N(-d1)

        Args:
            Same as calculate_call_option

        Returns:
            Dictionary with option_price, d1, d2, and greeks
        """
        # Handle edge case: expired option
        if time_to_maturity_years <= 0:
            intrinsic_value = max(0, strike_price - spot_rate)
            return {
                "option_price": intrinsic_value,
                "d1": 0,
                "d2": 0,
                "greeks": {"delta": -1 if strike_price > spot_rate else 0, "gamma": 0, "vega": 0, "theta": 0},
            }

        # Calculate d1 and d2 (same as call)
        sqrt_T = np.sqrt(time_to_maturity_years)
        vol_sqrt_T = volatility * sqrt_T

        forward_spot = spot_rate * np.exp(-foreign_rate * time_to_maturity_years)
        forward_strike = strike_price * np.exp(-domestic_rate * time_to_maturity_years)

        numerator = np.log(forward_spot / forward_strike)
        d1 = (numerator / vol_sqrt_T) + (vol_sqrt_T / 2)
        d2 = d1 - vol_sqrt_T

        # Calculate put price using N(-d1) and N(-d2)
        N_neg_d1 = cumulative_normal(-d1)
        N_neg_d2 = cumulative_normal(-d2)

        discount_foreign = np.exp(-foreign_rate * time_to_maturity_years)
        discount_domestic = np.exp(-domestic_rate * time_to_maturity_years)

        term1 = strike_price * discount_domestic * N_neg_d2
        term2 = discount_foreign * spot_rate * N_neg_d1

        option_price = term1 - term2

        # Calculate Greeks (put option greeks)
        delta = -discount_foreign * N_neg_d1

        pdf_d1 = probability_density_normal(d1)
        gamma = (discount_foreign * pdf_d1) / (spot_rate * vol_sqrt_T)

        vega = spot_rate * discount_foreign * pdf_d1 * sqrt_T

        theta_annual = (
            -(spot_rate * pdf_d1 * volatility * discount_foreign) / (2 * sqrt_T)
            - foreign_rate * spot_rate * N_neg_d1 * discount_foreign
            + domestic_rate * strike_price * discount_domestic * N_neg_d2
        )
        theta_daily = theta_annual / 365

        greeks = {
            "delta": float(delta),
            "gamma": float(gamma),
            "vega": float(vega / 100),
            "theta": float(theta_daily),
        }

        return {
            "option_price": float(option_price),
            "d1": float(d1),
            "d2": float(d2),
            "greeks": greeks,
        }

    @classmethod
    def price_with_analytics(
        cls,
        spot_rate: float,
        strike_price: float,
        time_to_maturity_years: float,
        volatility: float,
        domestic_rate: float,
        foreign_rate: float,
        notional_amount: float,
        option_type: str = "call",
        protection_level: float = 0.05,
    ) -> PricingResponse:
        """
        Calculate option price with full analytics for the UI.

        This method returns everything needed for the frontend:
        - Option price and cost
        - Greeks
        - Scenario analysis
        - Payoff curve data

        Args:
            spot_rate: Current spot rate
            strike_price: Strike price (if provided)
            time_to_maturity_years: Time to maturity
            volatility: Annualized volatility
            domestic_rate: Domestic risk-free rate
            foreign_rate: Foreign risk-free rate
            notional_amount: Notional amount in foreign currency
            option_type: "call" or "put"
            protection_level: Protection level (e.g., 0.05 for 5%)

        Returns:
            PricingResponse with all analytics
        """
        # Calculate strike if not provided
        if strike_price is None:
            if option_type == "call":
                # For call (importer): strike above spot
                strike_price = spot_rate * (1 + protection_level)
            else:
                # For put (exporter): strike below spot
                strike_price = spot_rate * (1 - protection_level)

        # Price the option
        if option_type == "call":
            result = cls.calculate_call_option(
                spot_rate, strike_price, time_to_maturity_years, volatility, domestic_rate, foreign_rate
            )
        else:
            result = cls.calculate_put_option(
                spot_rate, strike_price, time_to_maturity_years, volatility, domestic_rate, foreign_rate
            )

        option_price_per_unit = result["option_price"]
        total_option_cost = option_price_per_unit * notional_amount
        cost_percentage = (total_option_cost / (spot_rate * notional_amount)) * 100

        # Maximum cost to firm
        max_cost_to_firm = strike_price * notional_amount

        # Scenario analysis at different future spot rates
        scenarios = []
        for pct_change in [-0.10, -0.05, 0, 0.05, 0.10]:
            future_spot = spot_rate * (1 + pct_change)

            # Unhedged cost (for importer, paying at future spot rate)
            unhedged_cost = future_spot * notional_amount

            # Option payoff
            if option_type == "call":
                option_payoff = max(0, future_spot - strike_price) * notional_amount
            else:
                option_payoff = max(0, strike_price - future_spot) * notional_amount

            # Net cost = payment at spot + option premium - option payoff
            net_cost = unhedged_cost + total_option_cost - option_payoff

            savings = unhedged_cost - net_cost

            scenarios.append(
                ScenarioAnalysis(
                    future_spot_rate=future_spot,
                    unhedged_cost=unhedged_cost,
                    option_payoff=option_payoff,
                    net_cost=net_cost,
                    savings_vs_unhedged=savings,
                )
            )

        # Generate payoff curve for visualization
        payoff_curve = []
        spot_range = np.linspace(spot_rate * 0.85, spot_rate * 1.15, 50)

        for future_spot in spot_range:
            # Unhedged P&L (relative to current spot)
            unhedged_pnl = (future_spot - spot_rate) * notional_amount

            # Option payoff
            if option_type == "call":
                option_payoff = max(0, future_spot - strike_price) * notional_amount
            else:
                option_payoff = max(0, strike_price - future_spot) * notional_amount

            # Net P&L = unhedged + option payoff - premium
            net_pnl = unhedged_pnl + option_payoff - total_option_cost

            payoff_curve.append(
                PayoffCurvePoint(
                    spot_rate=float(future_spot),
                    unhedged_pnl=float(unhedged_pnl),
                    option_payoff=float(option_payoff),
                    net_pnl=float(net_pnl),
                )
            )

        # Break-even rate (where net cost = unhedged cost)
        # For call: breakeven approximately at spot + (premium/notional)
        breakeven_rate = spot_rate + (total_option_cost / notional_amount)

        return PricingResponse(
            option_price_per_unit=option_price_per_unit,
            total_option_cost=total_option_cost,
            cost_percentage=cost_percentage,
            strike_price=strike_price,
            protection_level=protection_level,
            max_cost_to_firm=max_cost_to_firm,
            d1=result["d1"],
            d2=result["d2"],
            greeks=Greeks(**result["greeks"]),
            scenarios=scenarios,
            payoff_curve=payoff_curve,
            breakeven_rate=breakeven_rate,
        )
