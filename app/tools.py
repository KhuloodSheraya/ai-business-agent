from typing import Optional

INVOICES = [
    {"id": "INV-1001", "customer": "Acme Clinic", "amount": 1250.0, "status": "overdue"},
    {"id": "INV-1002", "customer": "Nova Health", "amount": 890.0, "status": "paid"},
    {"id": "INV-1003", "customer": "Bright Labs", "amount": 2100.0, "status": "overdue"},
]

def search_invoices(status: Optional[str] = None, customer: Optional[str] = None, invoice_id: Optional[str] = None):
    results = INVOICES

    if status:
        results = [i for i in results if i["status"].lower() == status.lower()]

    if customer:
        results = [i for i in results if customer.lower() in i["customer"].lower()]

    if invoice_id:
        results = [i for i in results if i["id"].lower() == invoice_id.lower()]

    return {"count": len(results), "invoices": results}

def summarize_invoices(status: Optional[str] = None, customer: Optional[str] = None):
    results = search_invoices(status=status, customer=customer)["invoices"]
    return {
        "count": len(results),
        "total_amount": sum(i["amount"] for i in results),
    }

TOOLS = {
    "search_invoices": search_invoices,
    "summarize_invoices": summarize_invoices,
}
