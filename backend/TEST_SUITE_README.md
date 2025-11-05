# FX Hedging Platform - Test Suite

## Overview
Comprehensive test suite for validating all backend API endpoints and core functionality.

## Test Coverage

### 1. Demo Currency Seeding (3 tests)
- ✓ Successful currency seeding
- ✓ Idempotent seeding (safe to run multiple times)
- ✓ Currency list retrieval after seeding

### 2. Demo Transaction Generation (3 tests)
- ✓ Generate all demo scenarios
- ✓ Generate limited number of transactions
- ✓ Reset demo data

### 3. Pricing Calculation - Manual (6 tests)
- ✓ Valid call option pricing
- ✓ Valid put option pricing
- ✓ Missing required field validation
- ✓ Invalid option type validation
- ✓ Zero volatility edge case
- ✓ Negative time to maturity validation

### 4. Pricing Calculation - Auto (3 tests)
- ✓ Auto-calculate with valid currency pair
- ✓ Handle non-existent currencies
- ✓ Missing parameter validation

### 5. Exchange Rate Fallback Mechanism (5 tests)
- ✓ Get current rate from cache
- ✓ Force refresh from API
- ✓ Invalid currency pair handling
- ✓ Refresh rate endpoint
- ✓ Historical rates retrieval

### 6. Volatility Calculation (4 tests)
- ✓ Calculate volatility for valid pair
- ✓ Invalid currency pair format
- ✓ Custom lookback period
- ✓ Volatility calculation endpoint

### 7. Database Operations (4 tests)
- ✓ Currency persistence
- ✓ Transaction persistence
- ✓ Exchange rate caching
- ✓ Demo data cleanup

### 8. Error Handling (5 tests)
- ✓ Health check endpoint
- ✓ Root endpoint
- ✓ Invalid endpoint (404)
- ✓ Invalid HTTP method (405)
- ✓ Malformed JSON handling

### 9. Integration Workflow (1 test)
- ✓ Complete demo workflow (seed → generate → price → cleanup)

**Total: 34 tests**

## Running Tests

### Prerequisites
1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Install test dependencies (if not already installed):
```bash
pip install pytest httpx
```

### Run All Tests
```bash
pytest test_endpoints.py -v
```

### Run Specific Test Class
```bash
pytest test_endpoints.py::TestPricingCalculationManual -v
```

### Run Specific Test
```bash
pytest test_endpoints.py::TestPricingCalculationManual::test_pricing_calculate_valid_call_option -v
```

### Run with Detailed Output
```bash
pytest test_endpoints.py -v --tb=short
```

### Run and Show Print Statements
```bash
pytest test_endpoints.py -v -s
```

## Test Architecture

### Fixtures
- `api_client`: HTTP client for making API requests
- `ensure_server_running`: Validates server is running before tests

### Test Organization
Tests are organized into logical classes:
- Each class focuses on a specific area of functionality
- Tests within classes are related and may share setup
- Clear naming convention: `test_<feature>_<scenario>`

### Error Handling Strategy
- Tests gracefully handle missing API keys
- Tests expect specific HTTP status codes
- Tests validate both success and error responses
- Edge cases and boundary conditions are tested

## Expected Behavior

### Success Cases
- Tests validate response structure
- Tests check data types and ranges
- Tests verify business logic

### Error Cases
- 422: Validation errors (malformed input)
- 404: Resource not found
- 405: Method not allowed
- 500: Server errors (handled gracefully)

## Notes

### API Key Requirements
Some tests may fail if external API keys are not configured:
- Exchange rate refresh endpoints
- Historical data fetching
- Volatility calculation (requires historical data)

These failures are expected and handled gracefully by the tests.

### Database State
Tests use the actual database and may leave data behind. 
Use the `/api/demo/reset` endpoint to clean up between test runs.

### Performance
- Most tests complete in < 1 second
- Historical data tests may take longer
- Total suite runtime: ~5-15 seconds (depending on API calls)

## Maintenance

### Adding New Tests
1. Add test methods to appropriate class
2. Follow naming convention: `test_<feature>_<scenario>`
3. Include docstring explaining what is tested
4. Validate both success and error cases

### Debugging Failed Tests
```bash
pytest test_endpoints.py::TestClassName::test_name -v --tb=long
```

This shows full traceback and request/response details.
