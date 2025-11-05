# Integration Guide: FX Hedging Platform

This guide explains how to integrate the FX Hedging Platform with various accounting software systems, with a focus on Odoo (the dominant ERP in Latin America).

---

## Table of Contents

1. [Odoo Integration](#odoo-integration)
2. [QuickBooks Integration](#quickbooks-integration)
3. [SAP Integration](#sap-integration)
4. [Generic REST API Integration](#generic-rest-api-integration)
5. [Webhook Security](#webhook-security)
6. [Testing Integrations](#testing-integrations)

---

## Odoo Integration

### Overview

Odoo is the #1 ERP in Latin America. Our platform provides native Odoo integration that automatically detects foreign currency invoices with payment delays and creates hedging proposals.

### Prerequisites

- Odoo 14+ (Community or Enterprise)
- Admin access to Odoo instance
- API key from FX Hedging Platform

### Step 1: Get API Key

1. Contact FX Hedging Platform support
2. Receive API key (format: `odoo_integration_key`)
3. Store securely (do not commit to version control)

### Step 2: Configure Odoo Automated Action

**Navigation**: Settings → Technical → Automation → Automated Actions

**Create New Action**:

| Field | Value |
|-------|-------|
| Name | FX Hedging Platform - Foreign Currency Invoices |
| Model | Invoice (account.move) |
| Trigger | On Creation and Update |
| Apply on | Custom Domain |

**Domain Filter** (only foreign currency invoices):
```python
[
    ('currency_id', '!=', 'company_currency_id'),
    ('invoice_date_due', '>', 'invoice_date'),
    ('state', 'in', ['posted', 'approved']),
    ('move_type', 'in', ['out_invoice', 'in_invoice'])
]
```

**Action Type**: Execute Python Code

**Python Code**:
```python
import requests
import json
import logging

_logger = logging.getLogger(__name__)

# Configuration
FX_PLATFORM_URL = "https://your-platform.com/api/integrations/odoo/transactions"
API_KEY = env['ir.config_parameter'].sudo().get_param('fx_hedging.api_key')

if not API_KEY:
    _logger.error("FX Hedging API key not configured")
    raise UserError("FX Hedging API key not configured in System Parameters")

# Prepare invoice data
invoice_data = {
    "invoices": [{
        "id": record.id,
        "number": record.name,
        "date_invoice": record.invoice_date.strftime("%Y-%m-%d"),
        "date_due": record.invoice_date_due.strftime("%Y-%m-%d"),
        "currency_id": [record.currency_id.id, record.currency_id.name],
        "company_currency_id": [record.company_currency_id.id, record.company_currency_id.name],
        "amount_total": record.amount_total,
        "type": record.move_type,
        "partner_id": [record.partner_id.id, record.partner_id.name],
        "name": record.invoice_origin or record.ref or record.name
    }]
}

# Send to FX Hedging Platform
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

try:
    response = requests.post(FX_PLATFORM_URL, headers=headers, json=invoice_data, timeout=10)
    response.raise_for_status()

    _logger.info(f"Successfully sent invoice {record.name} to FX Hedging Platform")

    # Optional: Add note to invoice
    record.message_post(
        body=f"Invoice sent to FX Hedging Platform for FX risk analysis",
        subject="FX Hedging"
    )

except requests.exceptions.RequestException as e:
    _logger.error(f"Failed to send invoice to FX Hedging Platform: {str(e)}")
    # Don't fail the invoice creation, just log the error
```

### Step 3: Configure API Key in Odoo

**Navigation**: Settings → Technical → Parameters → System Parameters

**Create Parameter**:
- Key: `fx_hedging.api_key`
- Value: `your_api_key_here`

### Step 4: Test Integration

1. Create a test invoice in Odoo:
   - Customer: Any
   - Currency: USD (or any foreign currency)
   - Invoice Date: Today
   - Due Date: 90 days from now
   - Amount: $10,000

2. Post the invoice

3. Check FX Hedging Platform:
   - Navigate to http://localhost:8000/api/transactions/
   - Verify transaction was created
   - Source should be "odoo"

### Step 5: Review Hedging Proposals

Transactions from Odoo will appear in the FX Hedging Platform dashboard. Users can:

1. View automatic hedge pricing
2. Adjust protection level (default: 5%)
3. Approve or reject hedge
4. Track all hedges for accounting reconciliation

---

## QuickBooks Integration

### Overview

QuickBooks Online (QBO) supports webhooks for real-time event notifications.

### Prerequisites

- QuickBooks Online Plus or Advanced
- Developer account at https://developer.intuit.com
- OAuth 2.0 credentials

### Integration Steps

1. **Create Intuit App**:
   - Go to https://developer.intuit.com
   - Create new app
   - Select "QuickBooks Online API"
   - Get Client ID and Client Secret

2. **Configure Webhook**:
   - In Intuit Developer Portal, set webhook URL:
     ```
     https://your-platform.com/api/integrations/generic/webhook
     ```
   - Subscribe to events:
     - Invoice Created
     - Invoice Updated
     - Bill Created
     - Bill Updated

3. **Map QuickBooks Fields**:
   ```python
   # QuickBooks webhook payload
   {
       "eventNotifications": [{
           "realmId": "123456",
           "dataChangeEvent": {
               "entities": [{
                   "name": "Invoice",
                   "id": "145",
                   "operation": "Create"
               }]
           }
       }]
   }
   ```

4. **Fetch Invoice Details** (on webhook receipt):
   ```python
   # Use QuickBooks API to get full invoice
   GET https://quickbooks.api.intuit.com/v3/company/{realmId}/invoice/{invoiceId}
   ```

5. **Transform to Generic Format**:
   ```json
   {
       "transactions": [{
           "type": "import",
           "invoice_date": "2024-03-01",
           "payment_date": "2024-06-01",
           "foreign_currency": "USD",
           "functional_currency": "MXN",
           "amount": 1000000.00,
           "invoice_number": "INV-1045",
           "description": "Machinery import"
       }]
   }
   ```

6. **Send to Platform**:
   ```bash
   curl -X POST https://your-platform.com/api/integrations/generic/webhook \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d @invoice_data.json
   ```

---

## SAP Integration

### Overview

SAP Business One and SAP S/4HANA support REST APIs and OData services.

### Integration via Service Layer (SAP Business One)

1. **Enable Service Layer**:
   - Install SAP Service Layer
   - Default URL: `https://sapserver:50000/b1s/v1/`

2. **Authenticate**:
   ```bash
   curl -X POST https://sapserver:50000/b1s/v1/Login \
     -H "Content-Type: application/json" \
     -d '{
       "CompanyDB": "SBODEMO",
       "UserName": "manager",
       "Password": "password"
     }'
   ```

3. **Query Foreign Currency Invoices**:
   ```bash
   curl https://sapserver:50000/b1s/v1/Invoices \
     -H "Cookie: B1SESSION=..." \
     -G --data-urlencode '$filter=DocCurrency ne "MXN"'
   ```

4. **Transform and Send**:
   - Parse SAP invoice response
   - Map to generic format
   - POST to `/api/integrations/generic/webhook`

### Integration via RFC (SAP ERP)

For SAP ERP (not S/4HANA), use RFC (Remote Function Call):

1. Install SAP JCo (Java Connector) or PyRFC (Python)
2. Create custom RFC function module in SAP
3. Call FX Hedging Platform API from within SAP ABAP code

---

## Generic REST API Integration

For any accounting platform with REST API or webhook capability.

### Step 1: Understand Your Accounting Software's API

Required information:
- Which events trigger webhooks? (Invoice created, updated, etc.)
- What authentication method? (API key, OAuth, JWT)
- How to query invoices?
- What's the invoice data structure?

### Step 2: Create Middleware Script

Example in Python:

```python
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

FX_PLATFORM_URL = "https://your-platform.com/api/integrations/generic/webhook"
FX_API_KEY = "your_api_key"

@app.route('/accounting-webhook', methods=['POST'])
def handle_accounting_webhook():
    """Receive webhook from accounting software."""

    # Parse incoming webhook
    data = request.json

    # Transform to FX Platform format
    transactions = []

    for invoice in data.get('invoices', []):
        # Customize this mapping for your accounting software
        transaction = {
            "type": "import" if invoice['type'] == 'bill' else "export",
            "invoice_date": invoice['date'],
            "payment_date": invoice['due_date'],
            "foreign_currency": invoice['currency'],
            "functional_currency": "MXN",  # Your functional currency
            "amount": float(invoice['total']),
            "invoice_number": invoice['number'],
            "description": invoice['description']
        }

        # Only include foreign currency transactions
        if transaction['foreign_currency'] != transaction['functional_currency']:
            transactions.append(transaction)

    # Send to FX Hedging Platform
    if transactions:
        response = requests.post(
            FX_PLATFORM_URL,
            headers={"X-API-Key": FX_API_KEY, "Content-Type": "application/json"},
            json={"transactions": transactions}
        )

        return jsonify({"status": "success", "count": len(transactions)}), 200

    return jsonify({"status": "no_fx_transactions"}), 200

if __name__ == '__main__':
    app.run(port=5000)
```

### Step 3: Deploy Middleware

- Deploy on Heroku, AWS Lambda, or your own server
- Ensure HTTPS for security
- Set up monitoring and logging

### Step 4: Configure Webhook in Accounting Software

Point your accounting software's webhook to your middleware:
```
https://your-middleware.com/accounting-webhook
```

---

## Webhook Security

### Best Practices

1. **Use HTTPS Only**
   - Never send API keys over HTTP
   - Use TLS 1.2 or higher

2. **API Key Authentication**
   - Include API key in `X-API-Key` header
   - Rotate keys every 90 days
   - Use different keys for dev/staging/production

3. **IP Whitelisting** (optional but recommended)
   ```python
   ALLOWED_IPS = ['52.12.34.56', '54.23.45.67']  # Your accounting software IPs

   @app.before_request
   def check_ip():
       if request.remote_addr not in ALLOWED_IPS:
           abort(403)
   ```

4. **Request Signing** (advanced)
   ```python
   import hmac
   import hashlib

   SECRET = "your_webhook_secret"

   # Sender computes signature
   payload = json.dumps(data)
   signature = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

   # Include in header
   headers = {"X-Webhook-Signature": signature}

   # Receiver verifies
   computed_sig = hmac.new(SECRET.encode(), request.data, hashlib.sha256).hexdigest()
   if not hmac.compare_digest(computed_sig, request.headers.get('X-Webhook-Signature', '')):
       abort(401)
   ```

5. **Rate Limiting**
   - Limit to 100 requests/minute per API key
   - Return HTTP 429 if exceeded

6. **Logging and Monitoring**
   - Log all webhook requests
   - Alert on failures
   - Monitor for suspicious patterns

---

## Testing Integrations

### Test Endpoint

Use the test endpoint to verify integration without authentication:

```bash
curl -X POST http://localhost:8000/api/integrations/test?platform=odoo
```

Expected response:
```json
{
    "message": "Test odoo integration successful",
    "transactions": [{
        "id": 123,
        "transaction_type": "import",
        "foreign_currency": "USD",
        "functional_currency": "MXN",
        "notional_amount": 100000.00,
        "source": "test-odoo"
    }]
}
```

### Manual Testing with cURL

**Odoo Format**:
```bash
curl -X POST http://localhost:8000/api/integrations/odoo/transactions \
  -H "X-API-Key: demo_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "invoices": [{
      "id": 999,
      "number": "TEST/2024/0001",
      "date_invoice": "2024-03-01",
      "date_due": "2024-06-01",
      "currency_id": [2, "USD"],
      "company_currency_id": [1, "MXN"],
      "amount_total": 1000000.00,
      "type": "in_invoice",
      "name": "Test machinery import"
    }]
  }'
```

**Generic Format**:
```bash
curl -X POST http://localhost:8000/api/integrations/generic/webhook \
  -H "X-API-Key: demo_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [{
      "type": "import",
      "invoice_date": "2024-03-01",
      "payment_date": "2024-06-01",
      "foreign_currency": "USD",
      "functional_currency": "MXN",
      "amount": 1000000.00,
      "invoice_number": "TEST-001",
      "description": "Test import"
    }]
  }'
```

### Verify Integration Status

```bash
curl http://localhost:8000/api/integrations/status \
  -H "X-API-Key: demo_key_12345"
```

Expected response:
```json
{
    "status": "operational",
    "client": "Demo Client",
    "endpoints": {
        "odoo": "/api/integrations/odoo/transactions",
        "generic": "/api/integrations/generic/webhook"
    },
    "supported_platforms": [
        "Odoo",
        "QuickBooks Online",
        "SAP Business One",
        "Oracle NetSuite",
        "Microsoft Dynamics 365",
        "Xero",
        "Custom (via generic webhook)"
    ]
}
```

---

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check API key is correct
   - Ensure `X-API-Key` header is included
   - Verify key hasn't expired

2. **400 Bad Request**
   - Validate JSON format
   - Check required fields are present
   - Verify date format is YYYY-MM-DD

3. **500 Internal Server Error**
   - Check server logs
   - Verify database connection
   - Contact support with request ID

### Logging

Check integration logs:
```bash
docker-compose logs -f backend | grep "integration"
```

### Support

For integration assistance:
- Email: integrations@fxhedging.com
- Documentation: https://docs.fxhedging.com
- Status Page: https://status.fxhedging.com

---

## Future Integrations

Planned integrations:
- Contpaqi (Mexico) - Q2 2024
- Siigo (Colombia, Ecuador, Uruguay) - Q2 2024
- Totvs (Brazil) - Q3 2024
- Microsoft Dynamics 365 - Q3 2024
- Oracle NetSuite - Q4 2024

Request a new integration: integrations@fxhedging.com
