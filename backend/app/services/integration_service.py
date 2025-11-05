"""
Integration service for accounting software (Odoo, QuickBooks, etc.)

This service handles parsing and transformation of data from various
accounting platforms into our standardized Transaction format.
"""
from typing import List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from app.models.transaction import Transaction, TransactionType


class OdooIntegrationService:
    """
    Service for Odoo integration.

    Odoo is the dominant ERP in Latin America. This service parses
    Odoo's multi-currency transaction JSON and creates Transaction objects.
    """

    @staticmethod
    def parse_odoo_invoice(odoo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Odoo invoice JSON to our transaction format.

        Odoo invoice structure (simplified):
        {
            "id": 123,
            "number": "INV/2024/0001",
            "date_invoice": "2024-03-01",
            "date_due": "2024-06-01",
            "currency_id": [2, "USD"],
            "company_currency_id": [1, "MXN"],
            "amount_total": 1000000.00,
            "type": "out_invoice",  # or "in_invoice"
            "partner_id": [456, "Client Name"],
            "name": "Invoice description"
        }

        Args:
            odoo_data: Raw Odoo invoice JSON

        Returns:
            Dict compatible with TransactionCreate schema
        """
        # Determine transaction type
        # out_invoice = we're selling (export) = receiving foreign currency
        # in_invoice = we're buying (import) = paying foreign currency
        odoo_type = odoo_data.get("type", "in_invoice")
        transaction_type = "export" if odoo_type == "out_invoice" else "import"

        # Extract currency codes
        # Odoo stores currencies as [id, "CODE"]
        foreign_currency_tuple = odoo_data.get("currency_id", [None, "USD"])
        functional_currency_tuple = odoo_data.get("company_currency_id", [None, "MXN"])

        foreign_currency = foreign_currency_tuple[1] if isinstance(foreign_currency_tuple, list) else "USD"
        functional_currency = functional_currency_tuple[1] if isinstance(functional_currency_tuple, list) else "MXN"

        # Parse dates
        invoice_date_str = odoo_data.get("date_invoice") or odoo_data.get("invoice_date")
        due_date_str = odoo_data.get("date_due") or odoo_data.get("invoice_date_due")

        # Convert to date objects
        invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d").date() if invoice_date_str else date.today()
        payment_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else invoice_date

        # Extract amount
        amount = Decimal(str(odoo_data.get("amount_total", 0)))

        # Extract invoice reference
        invoice_reference = odoo_data.get("number") or odoo_data.get("name") or f"ODOO-{odoo_data.get('id')}"

        # Extract description
        description = odoo_data.get("name") or odoo_data.get("reference") or "Imported from Odoo"

        # Extract exchange rate if available
        spot_rate = None
        if "currency_rate" in odoo_data:
            spot_rate = Decimal(str(odoo_data["currency_rate"]))

        return {
            "transaction_type": transaction_type,
            "invoice_date": invoice_date,
            "payment_date": payment_date,
            "foreign_currency": foreign_currency,
            "functional_currency": functional_currency,
            "notional_amount": amount,
            "spot_rate_at_invoice": spot_rate,
            "invoice_reference": invoice_reference,
            "description": description,
            "source": "odoo"
        }

    @staticmethod
    def parse_odoo_batch(odoo_invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse multiple Odoo invoices.

        Args:
            odoo_invoices: List of Odoo invoice JSON objects

        Returns:
            List of transaction dicts
        """
        transactions = []

        for invoice in odoo_invoices:
            try:
                # Only process invoices with foreign currency
                currency_id = invoice.get("currency_id", [None, "MXN"])
                company_currency_id = invoice.get("company_currency_id", [None, "MXN"])

                foreign_curr = currency_id[1] if isinstance(currency_id, list) else currency_id
                functional_curr = company_currency_id[1] if isinstance(company_currency_id, list) else company_currency_id

                # Skip if same currency (no FX risk)
                if foreign_curr == functional_curr:
                    continue

                transaction_data = OdooIntegrationService.parse_odoo_invoice(invoice)
                transactions.append(transaction_data)

            except Exception as e:
                # Log error but continue processing other invoices
                print(f"Error parsing Odoo invoice {invoice.get('id')}: {e}")
                continue

        return transactions


class GenericIntegrationService:
    """
    Generic integration service for other accounting platforms.

    Supports a standardized JSON format that can be easily mapped
    from QuickBooks, SAP, Oracle, etc.
    """

    @staticmethod
    def parse_generic_transaction(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse generic transaction JSON.

        Expected format:
        {
            "type": "import" or "export",
            "invoice_date": "2024-03-01",
            "payment_date": "2024-06-01",
            "foreign_currency": "USD",
            "functional_currency": "MXN",
            "amount": 1000000.00,
            "exchange_rate": 19.00,  # optional
            "invoice_number": "INV-001",
            "description": "Machinery import"
        }

        Args:
            data: Generic transaction JSON

        Returns:
            Dict compatible with TransactionCreate schema
        """
        # Parse dates
        invoice_date_str = data.get("invoice_date")
        payment_date_str = data.get("payment_date")

        invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d").date() if invoice_date_str else date.today()
        payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date() if payment_date_str else invoice_date

        return {
            "transaction_type": data.get("type", "import"),
            "invoice_date": invoice_date,
            "payment_date": payment_date,
            "foreign_currency": data.get("foreign_currency", "USD").upper(),
            "functional_currency": data.get("functional_currency", "MXN").upper(),
            "notional_amount": Decimal(str(data.get("amount", 0))),
            "spot_rate_at_invoice": Decimal(str(data["exchange_rate"])) if "exchange_rate" in data else None,
            "invoice_reference": data.get("invoice_number"),
            "description": data.get("description"),
            "source": data.get("source", "api")
        }

    @staticmethod
    def parse_generic_batch(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse multiple generic transactions."""
        return [
            GenericIntegrationService.parse_generic_transaction(txn)
            for txn in transactions
        ]


class IntegrationService:
    """
    Main integration service that routes to specific parsers.
    """

    def __init__(self):
        self.odoo_service = OdooIntegrationService()
        self.generic_service = GenericIntegrationService()

    def parse_transactions(self, data: Dict[str, Any], source: str = "generic") -> List[Dict[str, Any]]:
        """
        Parse transactions from any source.

        Args:
            data: Transaction data (could be single or batch)
            source: "odoo", "quickbooks", "generic", etc.

        Returns:
            List of transaction dicts ready for database insertion
        """
        if source.lower() == "odoo":
            # Odoo sends array of invoices
            invoices = data.get("invoices", [data]) if "invoices" in data else [data]
            return self.odoo_service.parse_odoo_batch(invoices)

        else:
            # Generic format
            transactions = data.get("transactions", [data]) if "transactions" in data else [data]
            return self.generic_service.parse_generic_batch(transactions)
