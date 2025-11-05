# API Reference

Complete reference for all FX Hedging Platform API endpoints.

**Base URL**: `http://localhost:8000` (development) or `https://api.yourdomain.com` (production)

**Interactive Documentation**: http://localhost:8000/docs

---

## Authentication

Most endpoints are public in MVP. Integration endpoints require API key.

```http
X-API-Key: your_api_key_here
```

---

## Exchange Rates

### Get Current Rate

```http
GET /api/rates/current?base={base}&quote={quote}
```

**Parameters**:
- `base` (required): Base currency code (e.g., "USD")
- `quote` (required): Quote currency code (e.g., "MXN")
- `force_refresh` (optional): Force API fetch (default: false)

**Response**:
```json
{
  "base_currency": "USD",
  "quote_currency": "MXN",
  "rate": 19.2340,
  "description": "1 USD = 19.2340 MXN"
}
```

### Get Historical Rates

```http
GET /api/rates/historical?base={base}&quote={quote}&start_date={date}&end_date={date}
```

**Response**:
```json
{
  "base_currency": "USD",
  "quote_currency": "MXN",
  "count": 90,
  "rates": [
    {"date": "2024-01-01", "rate": 18.95},
    {"date": "2024-01-02", "rate": 19.01}
  ]
}
```

---

## Volatility

### Get Volatility

```http
GET /api/volatility/{currency_pair}
```

**Parameters**:
- `currency_pair` (path): e.g., "USDMXN"
- `force_recalculate` (query): Recalculate (default: false)
- `lookback_days` (query): Lookback period (default: 90)

**Response**:
```json
{
  "currency_pair": "USDMXN",
  "volatility": 0.2134,
  "volatility_percentage": 21.34,
  "lookback_days": 90,
  "method": "90-day historical"
}
```

---

## Transactions

### List Transactions

```http
GET /api/transactions/
```

**Query Parameters**:
- `transaction_type`: "import" or "export"
- `foreign_currency`: Currency code filter
- `functional_currency`: Currency code filter
- `source`: "manual", "odoo", "api", "demo"

**Response**:
```json
[
  {
    "id": 1,
    "transaction_type": "import",
    "invoice_date": "2024-03-01",
    "payment_date": "2024-06-01",
    "foreign_currency": "USD",
    "functional_currency": "MXN",
    "notional_amount": 1000000.00,
    "invoice_reference": "INV-001",
    "source": "manual",
    "created_at": "2024-03-01T10:00:00Z"
  }
]
```

### Create Transaction

```http
POST /api/transactions/
```

**Request Body**:
```json
{
  "transaction_type": "import",
  "invoice_date": "2024-03-01",
  "payment_date": "2024-06-01",
  "foreign_currency": "USD",
  "functional_currency": "MXN",
  "notional_amount": 1000000.00,
  "invoice_reference": "INV-001",
  "description": "Machinery import"
}
```

### Bulk Upload

```http
POST /api/transactions/upload
```

**Request Body**:
```json
{
  "transactions": [
    {...},
    {...}
  ]
}
```

---

## Pricing (THE CORE!)

### Calculate Pricing

```http
POST /api/pricing/calculate
```

**Request Body**:
```json
{
  "spot_rate": 19.00,
  "strike_price": 19.95,
  "time_to_maturity_years": 0.25,
  "volatility": 0.20,
  "domestic_rate": 0.04,
  "foreign_rate": 0.07,
  "notional_amount": 1000000,
  "option_type": "call",
  "protection_level": 0.05
}
```

**Response**:
```json
{
  "option_price_per_unit": 0.343,
  "total_option_cost": 343000.00,
  "cost_percentage": 1.81,
  "strike_price": 19.95,
  "protection_level": 0.05,
  "max_cost_to_firm": 19950000.00,
  "d1": 0.1234,
  "d2": 0.0234,
  "greeks": {
    "delta": 0.4523,
    "gamma": 0.0234,
    "vega": 123.45,
    "theta": -45.67
  },
  "scenarios": [...],
  "payoff_curve": [...],
  "breakeven_rate": 19.343
}
```

### Calculate with Auto-Fetch

```http
POST /api/pricing/calculate-auto?base=USD&quote=MXN&time_to_maturity_years=0.25&notional_amount=1000000
```

Automatically fetches current spot rate, volatility, and risk-free rates.

---

## Hedges

### List Hedges

```http
GET /api/hedges/
```

**Query Parameters**:
- `status`: "proposed", "purchased", "expired", "exercised"

### Create Hedge

```http
POST /api/hedges/
```

**Request Body**:
```json
{
  "transaction_id": 1,
  "strike_price": 19.95,
  "option_price_per_unit": 0.343,
  "total_option_cost": 343000.00,
  "cost_percentage": 0.0181,
  "volatility_used": 0.20,
  "domestic_rate_used": 0.04,
  "foreign_rate_used": 0.07,
  "time_to_maturity_years": 0.25,
  "protection_level": 0.05
}
```

### Update Hedge Status

```http
PATCH /api/hedges/{id}/status
```

**Request Body**:
```json
{
  "status": "purchased"
}
```

---

## Portfolio

### Get Portfolio Summary

```http
GET /api/portfolio/summary
```

**Response**:
```json
{
  "total_transactions": 15,
  "total_hedges": 10,
  "total_premium_paid": 2500000.00,
  "total_notional_hedged": 15000000.00,
  "average_cost_percentage": 1.67,
  "exposures_by_currency": [...],
  "netting_opportunities": [...]
}
```

### Get Exposures

```http
GET /api/portfolio/exposures
```

Returns breakdown by currency pair.

### Get Netting Opportunities

```http
GET /api/portfolio/netting-opportunities
```

Identifies natural hedges (offsetting imports/exports).

---

## Integrations

### Odoo Integration

```http
POST /api/integrations/odoo/transactions
X-API-Key: your_api_key
```

**Request Body**:
```json
{
  "invoices": [
    {
      "id": 123,
      "number": "INV/2024/0001",
      "date_invoice": "2024-03-01",
      "date_due": "2024-06-01",
      "currency_id": [2, "USD"],
      "company_currency_id": [1, "MXN"],
      "amount_total": 1000000.00,
      "type": "in_invoice",
      "name": "Machinery import"
    }
  ]
}
```

### Generic Webhook

```http
POST /api/integrations/generic/webhook
X-API-Key: your_api_key
```

**Request Body**:
```json
{
  "transactions": [
    {
      "type": "import",
      "invoice_date": "2024-03-01",
      "payment_date": "2024-06-01",
      "foreign_currency": "USD",
      "functional_currency": "MXN",
      "amount": 1000000.00,
      "invoice_number": "INV-001"
    }
  ]
}
```

### Integration Status

```http
GET /api/integrations/status
X-API-Key: your_api_key
```

---

## Demo

### Generate Demo Data

```http
POST /api/demo/generate
```

Creates sample transactions for testing.

### Seed Currencies

```http
POST /api/demo/seed-currencies
```

Populates currency table with defaults.

### Reset Demo

```http
POST /api/demo/reset
```

Clears all demo data.

---

## Currencies

### List Currencies

```http
GET /api/currencies/
```

### Get Currency

```http
GET /api/currencies/{code}
```

### Create Currency

```http
POST /api/currencies/
```

**Request Body**:
```json
{
  "code": "MXN",
  "name": "Mexican Peso",
  "symbol": "$",
  "risk_free_rate": 0.09,
  "is_foreign": true
}
```

### Update Currency

```http
PATCH /api/currencies/{code}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes**:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthorized (missing/invalid API key)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

- **Free tier**: 100 requests/minute
- **Paid tier**: 1000 requests/minute
- **Response header**: `X-RateLimit-Remaining`

---

## Webhooks

Configure webhooks to receive notifications:

```http
POST https://your-webhook-url.com
Content-Type: application/json

{
  "event": "hedge.created",
  "data": {...}
}
```

**Events**:
- `transaction.created`
- `hedge.proposed`
- `hedge.purchased`
- `hedge.expired`

---

## SDK Examples

### Python

```python
import requests

API_URL = "http://localhost:8000"

# Get current rate
response = requests.get(f"{API_URL}/api/rates/current", params={
    "base": "USD",
    "quote": "MXN"
})
rate = response.json()["rate"]

# Calculate pricing
pricing = requests.post(f"{API_URL}/api/pricing/calculate-auto", params={
    "base": "USD",
    "quote": "MXN",
    "time_to_maturity_years": 0.25,
    "notional_amount": 1000000
}).json()

print(f"Option cost: {pricing['total_option_cost']}")
```

### JavaScript

```javascript
const API_URL = "http://localhost:8000";

// Get current rate
const rateResponse = await fetch(
  `${API_URL}/api/rates/current?base=USD&quote=MXN`
);
const { rate } = await rateResponse.json();

// Calculate pricing
const pricingResponse = await fetch(
  `${API_URL}/api/pricing/calculate-auto?` +
  new URLSearchParams({
    base: "USD",
    quote: "MXN",
    time_to_maturity_years: 0.25,
    notional_amount: 1000000
  }),
  { method: "POST" }
);
const pricing = await pricingResponse.json();

console.log(`Option cost: ${pricing.total_option_cost}`);
```

---

## Support

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Email**: api@fxhedging.com
