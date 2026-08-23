from app.tools import search_invoices, summarize_invoices

def test_all_invoices():
    assert search_invoices()["count"] == 3

def test_overdue_invoices():
    assert search_invoices(status="overdue")["count"] == 2

def test_invoice_lookup():
    result = search_invoices(invoice_id="INV-1001")
    assert result["count"] == 1
    assert result["invoices"][0]["customer"] == "Acme Clinic"

def test_overdue_summary():
    result = summarize_invoices(status="overdue")
    assert result["total_amount"] == 3350.0
