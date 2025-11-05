"""
Unit tests for the Garman-Kohlhagen pricing engine.

CRITICAL: These tests verify the mathematical accuracy of our pricing model.
The test case from the requirements must pass exactly.
"""
import pytest
from app.services.pricing_engine import GarmanKohlhagenPricer


class TestGarmanKohlhagenPricer:
    """Test suite for the Garman-Kohlhagen option pricing engine."""

    def test_exact_formula_reference_case(self):
        """
        Test against the exact reference case from the requirements.

        Input:
        - S = 19 (MXN per USD)
        - K = 19.95 (5% protection)
        - T = 0.25 years (90 days)
        - σ = 0.20 (20% annual volatility)
        - r_domestic = 0.04 (4% MXN rate)
        - r_foreign = 0.07 (7% USD rate)

        Expected output:
        - Call option price ≈ 0.343 pesos per USD
        - For $1M notional: ~343,000 MXN
        - Cost as % of notional: ~1.8%
        """
        pricer = GarmanKohlhagenPricer()

        result = pricer.calculate_call_option(
            spot_rate=19.0,
            strike_price=19.95,
            time_to_maturity_years=0.25,
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        option_price = result["option_price"]

        # Verify price is approximately 0.343 (within 1% tolerance)
        assert abs(option_price - 0.343) < 0.01, f"Expected ~0.343, got {option_price}"

        # Verify d1 and d2 are calculated
        assert "d1" in result
        assert "d2" in result

        # Verify Greeks are present
        assert "greeks" in result
        assert "delta" in result["greeks"]
        assert "gamma" in result["greeks"]
        assert "vega" in result["greeks"]
        assert "theta" in result["greeks"]

        # Delta should be positive and < 1 for call option
        assert 0 < result["greeks"]["delta"] < 1

    def test_call_option_at_the_money(self):
        """Test call option when spot equals strike (at-the-money)."""
        pricer = GarmanKohlhagenPricer()

        result = pricer.calculate_call_option(
            spot_rate=20.0,
            strike_price=20.0,
            time_to_maturity_years=0.5,
            volatility=0.15,
            domestic_rate=0.05,
            foreign_rate=0.05,
        )

        # ATM option should have positive value
        assert result["option_price"] > 0

        # Delta should be around 0.5 for ATM call (with equal rates)
        assert 0.4 < result["greeks"]["delta"] < 0.6

    def test_call_option_deep_in_the_money(self):
        """Test call option deep in the money."""
        pricer = GarmanKohlhagenPricer()

        result = pricer.calculate_call_option(
            spot_rate=25.0,
            strike_price=20.0,  # Spot well above strike
            time_to_maturity_years=0.25,
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        # Deep ITM option should have high value
        assert result["option_price"] > 4.0  # Should be close to intrinsic value

        # Delta should be close to 1
        assert result["greeks"]["delta"] > 0.8

    def test_call_option_far_out_of_the_money(self):
        """Test call option far out of the money."""
        pricer = GarmanKohlhagenPricer()

        result = pricer.calculate_call_option(
            spot_rate=15.0,
            strike_price=20.0,  # Spot well below strike
            time_to_maturity_years=0.25,
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        # Far OTM option should have low value
        assert result["option_price"] < 0.5

        # Delta should be close to 0
        assert result["greeks"]["delta"] < 0.2

    def test_put_option_basic(self):
        """Test put option calculation."""
        pricer = GarmanKohlhagenPricer()

        result = pricer.calculate_put_option(
            spot_rate=19.0,
            strike_price=18.0,  # Below spot (for exporter protection)
            time_to_maturity_years=0.25,
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        # Put option should have positive value
        assert result["option_price"] > 0

        # Delta should be negative for put
        assert result["greeks"]["delta"] < 0

    def test_expired_option(self):
        """Test option at expiration (T=0)."""
        pricer = GarmanKohlhagenPricer()

        # Call option in the money at expiration
        result_itm = pricer.calculate_call_option(
            spot_rate=20.0,
            strike_price=19.0,
            time_to_maturity_years=0.0,
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        # Should equal intrinsic value
        assert abs(result_itm["option_price"] - 1.0) < 0.01

        # Call option out of the money at expiration
        result_otm = pricer.calculate_call_option(
            spot_rate=19.0,
            strike_price=20.0,
            time_to_maturity_years=0.0,
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        # Should be worthless
        assert result_otm["option_price"] == 0.0

    def test_price_with_analytics_full_output(self):
        """Test the full analytics pricing function."""
        pricer = GarmanKohlhagenPricer()

        result = pricer.price_with_analytics(
            spot_rate=19.0,
            strike_price=None,  # Will be calculated from protection_level
            time_to_maturity_years=0.25,
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
            notional_amount=1000000,
            option_type="call",
            protection_level=0.05,
        )

        # Verify all required fields are present
        assert result.option_price_per_unit > 0
        assert result.total_option_cost > 0
        assert result.cost_percentage < 3.0  # Should be under 3%
        assert result.strike_price == 19.95  # 5% above spot
        assert result.protection_level == 0.05
        assert result.max_cost_to_firm == 19.95 * 1000000

        # Verify Greeks
        assert result.greeks.delta > 0
        assert result.greeks.gamma > 0
        assert result.greeks.vega > 0

        # Verify scenarios are generated
        assert len(result.scenarios) == 5

        # Verify payoff curve is generated
        assert len(result.payoff_curve) == 50

        # Breakeven rate should be above spot
        assert result.breakeven_rate > 19.0

    def test_high_volatility_increases_price(self):
        """Higher volatility should increase option price."""
        pricer = GarmanKohlhagenPricer()

        low_vol_result = pricer.calculate_call_option(
            spot_rate=19.0,
            strike_price=19.95,
            time_to_maturity_years=0.25,
            volatility=0.10,  # Low volatility
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        high_vol_result = pricer.calculate_call_option(
            spot_rate=19.0,
            strike_price=19.95,
            time_to_maturity_years=0.25,
            volatility=0.30,  # High volatility
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        assert high_vol_result["option_price"] > low_vol_result["option_price"]

    def test_longer_maturity_increases_price(self):
        """Longer time to maturity should increase option price."""
        pricer = GarmanKohlhagenPricer()

        short_maturity_result = pricer.calculate_call_option(
            spot_rate=19.0,
            strike_price=19.95,
            time_to_maturity_years=0.08,  # ~1 month
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        long_maturity_result = pricer.calculate_call_option(
            spot_rate=19.0,
            strike_price=19.95,
            time_to_maturity_years=1.0,  # 1 year
            volatility=0.20,
            domestic_rate=0.04,
            foreign_rate=0.07,
        )

        assert long_maturity_result["option_price"] > short_maturity_result["option_price"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
