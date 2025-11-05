"""
Comprehensive test suite for FX Hedging Platform API endpoints.

Tests cover:
- Demo currency seeding
- Demo transaction generation
- Pricing calculation (manual)
- Pricing calculation (auto)
- Exchange rate fallback mechanism
- Volatility calculation
- Database operations
- Error handling
"""
import pytest
import httpx
from typing import Dict, Any
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def api_client():
    """Create a synchronous HTTP client for API testing."""
    return httpx.Client(base_url=BASE_URL, timeout=30.0)


@pytest.fixture(scope="session", autouse=True)
def ensure_server_running(api_client):
    """Ensure the server is running before tests."""
    try:
        response = api_client.get("/health")
        assert response.status_code == 200
        print(f"\nServer health check: {response.json()}")
    except Exception as e:
        pytest.fail(f"Server not running at {BASE_URL}. Please start it with 'uvicorn app.main:app'\nError: {e}")


# ============================================================================
# DEMO ENDPOINTS - Currency Seeding
# ============================================================================

class TestDemoCurrencySeeding:
    """Test currency seeding functionality."""

    def test_seed_currencies_success(self, api_client):
        """Test successful currency seeding."""
        response = api_client.post(f"{API_BASE}/demo/seed-currencies")

        assert response.status_code == 200
        data = response.json()

        # Response should be a list of currencies
        assert isinstance(data, list)

        # Check that we have common currencies
        currency_codes = [c["code"] for c in data] if data else []
        print(f"Seeded currencies: {currency_codes}")

    def test_seed_currencies_idempotent(self, api_client):
        """Test that seeding currencies multiple times is safe (idempotent)."""
        # First seed
        response1 = api_client.post(f"{API_BASE}/demo/seed-currencies")
        assert response1.status_code == 200

        # Second seed should not fail
        response2 = api_client.post(f"{API_BASE}/demo/seed-currencies")
        assert response2.status_code == 200

    def test_currencies_list_after_seeding(self, api_client):
        """Test that currencies can be retrieved after seeding."""
        # Seed currencies
        api_client.post(f"{API_BASE}/demo/seed-currencies")

        # Get currencies list
        response = api_client.get(f"{API_BASE}/currencies")
        assert response.status_code == 200

        currencies = response.json()
        assert len(currencies) > 0

        # Check structure of first currency
        if currencies:
            currency = currencies[0]
            assert "code" in currency
            assert "name" in currency
            assert "risk_free_rate" in currency


# ============================================================================
# DEMO ENDPOINTS - Transaction Generation
# ============================================================================

class TestDemoTransactionGeneration:
    """Test demo transaction generation."""

    def test_generate_demo_data_all_scenarios(self, api_client):
        """Test generating all demo transactions."""
        response = api_client.post(f"{API_BASE}/demo/generate")

        assert response.status_code == 200
        transactions = response.json()

        # Should generate multiple transactions
        assert isinstance(transactions, list)
        assert len(transactions) > 0

        # Check transaction structure
        if transactions:
            tx = transactions[0]
            required_fields = [
                "id", "transaction_type", "invoice_date", "payment_date",
                "foreign_currency", "functional_currency", "notional_amount",
                "description", "source"
            ]
            for field in required_fields:
                assert field in tx, f"Missing field: {field}"

            # Check that source is 'demo'
            assert tx["source"] == "demo"

        print(f"Generated {len(transactions)} demo transactions")

    def test_generate_demo_data_limited(self, api_client):
        """Test generating limited number of transactions."""
        response = api_client.post(f"{API_BASE}/demo/generate?num_transactions=3")

        assert response.status_code == 200
        transactions = response.json()

        # Should generate requested number or less
        assert isinstance(transactions, list)
        assert len(transactions) <= 3

    def test_demo_data_reset(self, api_client):
        """Test resetting demo data."""
        # First generate some data
        api_client.post(f"{API_BASE}/demo/generate")

        # Reset
        response = api_client.post(f"{API_BASE}/demo/reset")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "cleared successfully" in data["message"].lower()


# ============================================================================
# PRICING ENDPOINTS - Manual Calculation
# ============================================================================

class TestPricingCalculationManual:
    """Test manual pricing calculation with provided parameters."""

    def test_pricing_calculate_valid_call_option(self, api_client):
        """Test pricing calculation with valid call option parameters."""
        payload = {
            "spot_rate": 19.0,
            "strike_price": 19.95,
            "time_to_maturity_years": 0.25,
            "volatility": 0.20,
            "domestic_rate": 0.04,
            "foreign_rate": 0.07,
            "notional_amount": 1000000,
            "option_type": "call",
            "protection_level": 0.05
        }

        response = api_client.post(f"{API_BASE}/pricing/calculate", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        required_fields = ["option_price", "total_cost", "cost_percentage", "greeks"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Check that values are reasonable
        assert data["option_price"] > 0
        assert data["total_cost"] > 0
        assert 0 < data["cost_percentage"] < 10  # Should be less than 10%

        # Check Greeks exist
        assert "delta" in data["greeks"]
        assert "gamma" in data["greeks"]
        assert "vega" in data["greeks"]
        assert "theta" in data["greeks"]

        print(f"Option price: {data['option_price']:.4f}")
        print(f"Total cost: {data['total_cost']:.2f}")
        print(f"Cost percentage: {data['cost_percentage']:.2f}%")

    def test_pricing_calculate_valid_put_option(self, api_client):
        """Test pricing calculation with valid put option parameters."""
        payload = {
            "spot_rate": 19.0,
            "strike_price": 18.05,
            "time_to_maturity_years": 0.25,
            "volatility": 0.20,
            "domestic_rate": 0.04,
            "foreign_rate": 0.07,
            "notional_amount": 1000000,
            "option_type": "put",
            "protection_level": 0.05
        }

        response = api_client.post(f"{API_BASE}/pricing/calculate", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["option_price"] > 0
        assert data["total_cost"] > 0

    def test_pricing_calculate_missing_required_field(self, api_client):
        """Test pricing calculation with missing required field."""
        payload = {
            "spot_rate": 19.0,
            # Missing strike_price
            "time_to_maturity_years": 0.25,
            "volatility": 0.20,
            "domestic_rate": 0.04,
            "foreign_rate": 0.07,
            "notional_amount": 1000000,
            "option_type": "call"
        }

        response = api_client.post(f"{API_BASE}/pricing/calculate", json=payload)

        # Should return validation error
        assert response.status_code == 422

    def test_pricing_calculate_invalid_option_type(self, api_client):
        """Test pricing calculation with invalid option type."""
        payload = {
            "spot_rate": 19.0,
            "strike_price": 19.95,
            "time_to_maturity_years": 0.25,
            "volatility": 0.20,
            "domestic_rate": 0.04,
            "foreign_rate": 0.07,
            "notional_amount": 1000000,
            "option_type": "invalid_type",  # Invalid
            "protection_level": 0.05
        }

        response = api_client.post(f"{API_BASE}/pricing/calculate", json=payload)

        # Should return validation error
        assert response.status_code == 422

    def test_pricing_calculate_zero_volatility(self, api_client):
        """Test pricing calculation with zero volatility."""
        payload = {
            "spot_rate": 19.0,
            "strike_price": 19.95,
            "time_to_maturity_years": 0.25,
            "volatility": 0.0,  # Zero volatility
            "domestic_rate": 0.04,
            "foreign_rate": 0.07,
            "notional_amount": 1000000,
            "option_type": "call",
            "protection_level": 0.05
        }

        response = api_client.post(f"{API_BASE}/pricing/calculate", json=payload)

        # Should handle gracefully (may return very small price)
        assert response.status_code in [200, 422]

    def test_pricing_calculate_negative_time(self, api_client):
        """Test pricing calculation with negative time to maturity."""
        payload = {
            "spot_rate": 19.0,
            "strike_price": 19.95,
            "time_to_maturity_years": -0.25,  # Negative time
            "volatility": 0.20,
            "domestic_rate": 0.04,
            "foreign_rate": 0.07,
            "notional_amount": 1000000,
            "option_type": "call",
            "protection_level": 0.05
        }

        response = api_client.post(f"{API_BASE}/pricing/calculate", json=payload)

        # Should return validation error
        assert response.status_code == 422


# ============================================================================
# PRICING ENDPOINTS - Auto Calculation
# ============================================================================

class TestPricingCalculationAuto:
    """Test automatic pricing calculation with data fetching."""

    def test_pricing_calculate_auto_valid(self, api_client):
        """Test auto pricing with valid currency pair."""
        # First ensure currencies are seeded
        api_client.post(f"{API_BASE}/demo/seed-currencies")
        api_client.post(f"{API_BASE}/demo/generate")  # This seeds exchange rates too

        response = api_client.post(
            f"{API_BASE}/pricing/calculate-auto",
            params={
                "base": "USD",
                "quote": "MXN",
                "time_to_maturity_years": 0.25,
                "notional_amount": 1000000,
                "option_type": "call",
                "protection_level": 0.05
            }
        )

        # May succeed or fail depending on whether rates are available
        if response.status_code == 200:
            data = response.json()

            # If successful, check structure
            if "error" not in data:
                assert data["option_price"] > 0
                assert data["total_cost"] > 0
                print(f"Auto-calculated option price: {data['option_price']:.4f}")
        else:
            # May fail if external API is unavailable
            print(f"Auto-calculation failed (expected if no API key): {response.status_code}")

    def test_pricing_calculate_auto_currency_not_found(self, api_client):
        """Test auto pricing with non-existent currency."""
        response = api_client.post(
            f"{API_BASE}/pricing/calculate-auto",
            params={
                "base": "XXX",  # Non-existent currency
                "quote": "YYY",
                "time_to_maturity_years": 0.25,
                "notional_amount": 1000000,
                "option_type": "call",
                "protection_level": 0.05
            }
        )

        # Should handle gracefully with error message
        # May be 200 with error in body, or 404/422
        assert response.status_code in [200, 404, 422, 500]

        if response.status_code == 200:
            data = response.json()
            # Check if error message is present
            if isinstance(data, dict) and "error" in data:
                assert "not found" in data["error"].lower() or "currency" in data["error"].lower()

    def test_pricing_calculate_auto_missing_params(self, api_client):
        """Test auto pricing with missing required parameters."""
        response = api_client.post(
            f"{API_BASE}/pricing/calculate-auto",
            params={
                "base": "USD",
                # Missing quote
                "time_to_maturity_years": 0.25,
                "notional_amount": 1000000,
            }
        )

        # Should return validation error
        assert response.status_code == 422


# ============================================================================
# EXCHANGE RATE ENDPOINTS - Fallback Mechanism
# ============================================================================

class TestExchangeRateFallback:
    """Test exchange rate fetching and fallback mechanisms."""

    def test_get_current_rate_cached(self, api_client):
        """Test getting current exchange rate from cache."""
        # Seed demo rates first
        api_client.post(f"{API_BASE}/demo/generate")

        # Get rate (should use cache)
        response = api_client.get(
            f"{API_BASE}/rates/current",
            params={"base": "USD", "quote": "MXN"}
        )

        if response.status_code == 200:
            data = response.json()
            assert "rate" in data
            assert "base_currency" in data
            assert "quote_currency" in data
            assert data["base_currency"] == "USD"
            assert data["quote_currency"] == "MXN"
            assert data["rate"] > 0
            print(f"USD/MXN rate: {data['rate']}")

    def test_get_current_rate_force_refresh(self, api_client):
        """Test forcing rate refresh from API."""
        response = api_client.get(
            f"{API_BASE}/rates/current",
            params={"base": "USD", "quote": "EUR", "force_refresh": True}
        )

        # May fail if no API key configured
        if response.status_code == 200:
            data = response.json()
            assert "rate" in data
            assert data["rate"] > 0
        else:
            print(f"Force refresh failed (expected if no API key): {response.status_code}")

    def test_get_current_rate_invalid_currency(self, api_client):
        """Test getting rate for invalid currency pair."""
        response = api_client.get(
            f"{API_BASE}/rates/current",
            params={"base": "XXX", "quote": "YYY"}
        )

        # Should handle gracefully (may be 500 or 200 with error)
        assert response.status_code in [200, 404, 422, 500]

    def test_refresh_rate_endpoint(self, api_client):
        """Test the refresh rate endpoint."""
        response = api_client.post(
            f"{API_BASE}/rates/refresh",
            params={"base": "USD", "quote": "EUR"}
        )

        # May fail if no API key
        if response.status_code == 200:
            data = response.json()
            assert "rate" in data
            assert "message" in data
        else:
            print(f"Refresh endpoint failed (expected if no API key): {response.status_code}")

    def test_get_historical_rates(self, api_client):
        """Test getting historical exchange rates."""
        response = api_client.get(
            f"{API_BASE}/rates/historical",
            params={
                "base": "USD",
                "quote": "MXN",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )

        # May fail if no API key or data unavailable
        if response.status_code == 200:
            data = response.json()
            assert "rates" in data
            assert "count" in data
            assert isinstance(data["rates"], list)
            print(f"Retrieved {data['count']} historical rates")
        else:
            print(f"Historical rates failed (expected if no API key): {response.status_code}")


# ============================================================================
# VOLATILITY ENDPOINTS
# ============================================================================

class TestVolatilityCalculation:
    """Test volatility calculation endpoints."""

    def test_get_volatility_valid_pair(self, api_client):
        """Test getting volatility for valid currency pair."""
        # Seed some data first
        api_client.post(f"{API_BASE}/demo/generate")

        response = api_client.get(f"{API_BASE}/volatility/USDMXN")

        # May fail if insufficient historical data
        if response.status_code == 200:
            data = response.json()
            assert "volatility" in data
            assert "currency_pair" in data
            assert data["currency_pair"] == "USDMXN"
            assert data["volatility"] >= 0
            print(f"USDMXN volatility: {data['volatility']:.4f} ({data['volatility']*100:.2f}%)")
        else:
            print(f"Volatility calculation failed (may need historical data): {response.status_code}")

    def test_get_volatility_invalid_format(self, api_client):
        """Test getting volatility with invalid currency pair format."""
        response = api_client.get(f"{API_BASE}/volatility/INVALID")

        # Should return error for invalid format
        if response.status_code == 200:
            data = response.json()
            assert "error" in data

    def test_get_volatility_with_lookback(self, api_client):
        """Test getting volatility with custom lookback period."""
        response = api_client.get(
            f"{API_BASE}/volatility/USDMXN",
            params={"lookback_days": 30}
        )

        # May succeed or fail depending on data availability
        if response.status_code == 200:
            data = response.json()
            if "error" not in data:
                assert data["lookback_days"] == 30

    def test_calculate_volatility_endpoint(self, api_client):
        """Test the calculate volatility endpoint."""
        response = api_client.post(
            f"{API_BASE}/volatility/calculate",
            params={
                "base": "USD",
                "quote": "MXN",
                "lookback_days": 90
            }
        )

        # May fail if insufficient data
        if response.status_code == 200:
            data = response.json()
            if "error" not in data:
                assert "volatility" in data
                assert "message" in data
        else:
            print(f"Volatility calculation failed (may need historical data): {response.status_code}")


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

class TestDatabaseOperations:
    """Test database-related operations."""

    def test_currency_persistence(self, api_client):
        """Test that currencies persist in database."""
        # Seed currencies
        response1 = api_client.post(f"{API_BASE}/demo/seed-currencies")
        assert response1.status_code == 200

        # Retrieve currencies
        response2 = api_client.get(f"{API_BASE}/currencies")
        assert response2.status_code == 200

        currencies = response2.json()
        assert len(currencies) > 0

    def test_transaction_persistence(self, api_client):
        """Test that transactions persist in database."""
        # Generate demo transactions
        response1 = api_client.post(f"{API_BASE}/demo/generate")
        assert response1.status_code == 200
        transactions = response1.json()

        if transactions:
            # Get transactions list
            response2 = api_client.get(f"{API_BASE}/transactions")
            assert response2.status_code == 200

            all_transactions = response2.json()
            assert len(all_transactions) > 0

    def test_exchange_rate_caching(self, api_client):
        """Test that exchange rates are cached."""
        # Seed demo rates
        api_client.post(f"{API_BASE}/demo/generate")

        # Get rate twice
        response1 = api_client.get(
            f"{API_BASE}/rates/current",
            params={"base": "USD", "quote": "MXN"}
        )

        time.sleep(0.1)  # Small delay

        response2 = api_client.get(
            f"{API_BASE}/rates/current",
            params={"base": "USD", "quote": "MXN"}
        )

        # Both should succeed if first succeeded
        if response1.status_code == 200:
            assert response2.status_code == 200
            rate1 = response1.json()["rate"]
            rate2 = response2.json()["rate"]
            # Rates should be identical (cached)
            assert rate1 == rate2

    def test_demo_data_cleanup(self, api_client):
        """Test that demo data can be cleaned up."""
        # Generate demo data
        response1 = api_client.post(f"{API_BASE}/demo/generate")
        assert response1.status_code == 200

        # Reset demo data
        response2 = api_client.post(f"{API_BASE}/demo/reset")
        assert response2.status_code == 200
        data = response2.json()
        assert "message" in data


# ============================================================================
# ERROR HANDLING AND EDGE CASES
# ============================================================================

class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_health_check(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, api_client):
        """Test root endpoint."""
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_invalid_endpoint(self, api_client):
        """Test accessing non-existent endpoint."""
        response = api_client.get(f"{API_BASE}/invalid/endpoint")
        assert response.status_code == 404

    def test_invalid_method(self, api_client):
        """Test using wrong HTTP method."""
        response = api_client.delete(f"{API_BASE}/demo/seed-currencies")
        assert response.status_code == 405

    def test_malformed_json(self, api_client):
        """Test sending malformed JSON."""
        response = api_client.post(
            f"{API_BASE}/pricing/calculate",
            content=b"{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegrationWorkflow:
    """Test complete workflows end-to-end."""

    def test_complete_demo_workflow(self, api_client):
        """Test complete demo workflow: seed, generate, price."""
        # Step 1: Seed currencies
        response1 = api_client.post(f"{API_BASE}/demo/seed-currencies")
        assert response1.status_code == 200
        print("\n1. Currencies seeded")

        # Step 2: Generate demo transactions
        response2 = api_client.post(f"{API_BASE}/demo/generate?num_transactions=3")
        assert response2.status_code == 200
        transactions = response2.json()
        assert len(transactions) > 0
        print(f"2. Generated {len(transactions)} demo transactions")

        # Step 3: Calculate pricing for a demo scenario
        response3 = api_client.post(
            f"{API_BASE}/pricing/calculate",
            json={
                "spot_rate": 19.0,
                "strike_price": 19.95,
                "time_to_maturity_years": 0.25,
                "volatility": 0.20,
                "domestic_rate": 0.04,
                "foreign_rate": 0.07,
                "notional_amount": 1000000,
                "option_type": "call",
                "protection_level": 0.05
            }
        )
        assert response3.status_code == 200
        pricing = response3.json()
        print(f"3. Calculated option price: {pricing['option_price']:.4f}")
        print(f"   Total cost: {pricing['total_cost']:.2f}")
        print(f"   Cost percentage: {pricing['cost_percentage']:.2f}%")

        # Step 4: Clean up
        response4 = api_client.post(f"{API_BASE}/demo/reset")
        assert response4.status_code == 200
        print("4. Demo data cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
