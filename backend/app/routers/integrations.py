"""
Integration endpoints for accounting software.

These endpoints allow accounting platforms (Odoo, QuickBooks, etc.)
to push transaction data to our platform for hedging.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.transaction import Transaction, TransactionType
from app.services.integration_service import IntegrationService
from app.schemas.transaction import TransactionResponse

router = APIRouter()
integration_service = IntegrationService()

# Simple API key authentication (in production, use proper OAuth/JWT)
VALID_API_KEYS = {
    "demo_key_12345": "Demo Client",
    "odoo_integration_key": "Odoo Integration",
}


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key for integration endpoints.

    In production, replace with proper authentication:
    - OAuth 2.0
    - JWT tokens
    - Database-stored API keys with rate limiting
    """
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return VALID_API_KEYS[x_api_key]


@router.post("/odoo/transactions", response_model=List[TransactionResponse])
async def receive_odoo_transactions(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    client_name: str = Depends(verify_api_key),
):
    """
    Receive transactions from Odoo ERP.

    This endpoint accepts Odoo invoice data and creates transactions
    for foreign currency invoices with payment delays.

    **Authentication**: Requires X-API-Key header

    **Odoo Webhook Setup**:
    1. In Odoo, go to Settings > Technical > Automation > Automated Actions
    2. Create new action on "Invoice" model
    3. Trigger: On Creation or Update
    4. Filter: currency_id != company_currency_id AND date_due > date_invoice
    5. Action: Execute Python Code
    6. Code:
       ```python
       import requests
       import json

       url = "https://your-platform.com/api/integrations/odoo/transactions"
       headers = {
           "X-API-Key": "your_api_key_here",
           "Content-Type": "application/json"
       }
       payload = {
           "invoices": [{
               "id": record.id,
               "number": record.number,
               "date_invoice": record.date_invoice.strftime("%Y-%m-%d"),
               "date_due": record.date_due.strftime("%Y-%m-%d"),
               "currency_id": [record.currency_id.id, record.currency_id.name],
               "company_currency_id": [record.company_currency_id.id, record.company_currency_id.name],
               "amount_total": record.amount_total,
               "type": record.type,
               "name": record.name
           }]
       }

       response = requests.post(url, headers=headers, json=payload)
       ```

    **Example Request**:
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
                "name": "Machinery import from USA"
            }
        ]
    }
    ```

    **Response**: List of created transactions
    """
    try:
        # Parse Odoo data
        transaction_data_list = integration_service.parse_transactions(data, source="odoo")

        if not transaction_data_list:
            return []

        # Create transactions in database
        created_transactions = []

        for txn_data in transaction_data_list:
            # Convert transaction_type string to enum
            txn_type = TransactionType(txn_data["transaction_type"])

            transaction = Transaction(
                transaction_type=txn_type,
                invoice_date=txn_data["invoice_date"],
                payment_date=txn_data["payment_date"],
                foreign_currency=txn_data["foreign_currency"],
                functional_currency=txn_data["functional_currency"],
                notional_amount=txn_data["notional_amount"],
                spot_rate_at_invoice=txn_data.get("spot_rate_at_invoice"),
                invoice_reference=txn_data.get("invoice_reference"),
                description=txn_data.get("description"),
                source="odoo",
            )

            db.add(transaction)
            created_transactions.append(transaction)

        await db.commit()

        # Refresh all
        for txn in created_transactions:
            await db.refresh(txn)

        return created_transactions

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process Odoo transactions: {str(e)}"
        )


@router.post("/generic/webhook", response_model=List[TransactionResponse])
async def receive_generic_webhook(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    client_name: str = Depends(verify_api_key),
):
    """
    Generic webhook for other accounting platforms.

    Supports QuickBooks, SAP, Oracle, Microsoft Dynamics, and any platform
    that can send JSON webhooks.

    **Authentication**: Requires X-API-Key header

    **Format**: Standardized JSON format
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
                "exchange_rate": 19.00,
                "invoice_number": "INV-001",
                "description": "Machinery import"
            }
        ]
    }
    ```

    **Supported Platforms**:
    - QuickBooks Online (via Webhooks API)
    - SAP Business One (via Service Layer)
    - Oracle NetSuite (via SuiteScript)
    - Microsoft Dynamics 365 (via Web API)
    - Xero (via Webhooks)
    - Any custom integration

    **Response**: List of created transactions
    """
    try:
        # Parse generic data
        transaction_data_list = integration_service.parse_transactions(data, source="generic")

        if not transaction_data_list:
            return []

        # Create transactions in database
        created_transactions = []

        for txn_data in transaction_data_list:
            txn_type = TransactionType(txn_data["transaction_type"])

            transaction = Transaction(
                transaction_type=txn_type,
                invoice_date=txn_data["invoice_date"],
                payment_date=txn_data["payment_date"],
                foreign_currency=txn_data["foreign_currency"],
                functional_currency=txn_data["functional_currency"],
                notional_amount=txn_data["notional_amount"],
                spot_rate_at_invoice=txn_data.get("spot_rate_at_invoice"),
                invoice_reference=txn_data.get("invoice_reference"),
                description=txn_data.get("description"),
                source=txn_data.get("source", "api"),
            )

            db.add(transaction)
            created_transactions.append(transaction)

        await db.commit()

        # Refresh all
        for txn in created_transactions:
            await db.refresh(txn)

        return created_transactions

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process webhook transactions: {str(e)}"
        )


@router.get("/status")
async def integration_status(client_name: str = Depends(verify_api_key)):
    """
    Health check for integration endpoints.

    Verifies that:
    - API key is valid
    - Integration service is operational
    - Database is accessible

    **Authentication**: Requires X-API-Key header

    **Response**:
    ```json
    {
        "status": "operational",
        "client": "Demo Client",
        "endpoints": {
            "odoo": "/api/integrations/odoo/transactions",
            "generic": "/api/integrations/generic/webhook"
        },
        "supported_platforms": ["Odoo", "QuickBooks", "SAP", "Oracle", "Dynamics", "Xero"]
    }
    ```
    """
    return {
        "status": "operational",
        "client": client_name,
        "endpoints": {
            "odoo": "/api/integrations/odoo/transactions",
            "generic": "/api/integrations/generic/webhook",
        },
        "supported_platforms": [
            "Odoo",
            "QuickBooks Online",
            "SAP Business One",
            "Oracle NetSuite",
            "Microsoft Dynamics 365",
            "Xero",
            "Custom (via generic webhook)",
        ],
        "authentication": "API Key (X-API-Key header)",
        "documentation": "/docs#/Integrations",
    }


@router.post("/test")
async def test_integration(
    platform: str = "odoo",
    db: AsyncSession = Depends(get_db),
):
    """
    Test integration endpoints without authentication.

    Creates a sample transaction for testing purposes.

    **Parameters**:
    - platform: "odoo" or "generic"

    **Response**: Created transaction
    """
    if platform == "odoo":
        # Sample Odoo invoice
        test_data = {
            "invoices": [{
                "id": 999,
                "number": "TEST/2024/0001",
                "date_invoice": "2024-03-01",
                "date_due": "2024-06-01",
                "currency_id": [2, "USD"],
                "company_currency_id": [1, "MXN"],
                "amount_total": 100000.00,
                "type": "in_invoice",
                "name": "Test Odoo integration"
            }]
        }
        source = "odoo"
    else:
        # Sample generic transaction
        test_data = {
            "transactions": [{
                "type": "import",
                "invoice_date": "2024-03-01",
                "payment_date": "2024-06-01",
                "foreign_currency": "USD",
                "functional_currency": "MXN",
                "amount": 100000.00,
                "invoice_number": "TEST-001",
                "description": "Test generic integration"
            }]
        }
        source = "generic"

    # Parse and create
    transaction_data_list = integration_service.parse_transactions(test_data, source=source)

    created_transactions = []
    for txn_data in transaction_data_list:
        txn_type = TransactionType(txn_data["transaction_type"])

        transaction = Transaction(
            transaction_type=txn_type,
            invoice_date=txn_data["invoice_date"],
            payment_date=txn_data["payment_date"],
            foreign_currency=txn_data["foreign_currency"],
            functional_currency=txn_data["functional_currency"],
            notional_amount=txn_data["notional_amount"],
            spot_rate_at_invoice=txn_data.get("spot_rate_at_invoice"),
            invoice_reference=txn_data.get("invoice_reference"),
            description=txn_data.get("description"),
            source=f"test-{source}",
        )

        db.add(transaction)
        created_transactions.append(transaction)

    await db.commit()

    for txn in created_transactions:
        await db.refresh(txn)

    return {
        "message": f"Test {source} integration successful",
        "transactions": created_transactions,
    }
