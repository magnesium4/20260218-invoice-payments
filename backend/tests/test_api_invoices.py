import pytest
from decimal import Decimal
from datetime import datetime, timezone


def test_create_invoice(client, sample_customer):
    """Test creating a new invoice via API"""
    invoice_data = {
        "customer_id": sample_customer.id,
        "amount": "1500.00",
        "currency": "USD",
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "due_at": datetime.now(timezone.utc).isoformat(),
        "status": "DRAFT"
    }
    
    response = client.post("/invoices", json=invoice_data)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "1500.00"
    assert data["currency"] == "USD"
    assert data["customer_id"] == sample_customer.id


def test_get_invoice(client, sample_invoice):
    """Test getting an invoice by ID"""
    response = client.get(f"/invoices/{sample_invoice.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_invoice.id
    assert data["amount"] == "1000.00"


def test_get_invoice_not_found(client):
    """Test getting a non-existent invoice returns 404"""
    response = client.get("/invoices/99999")
    assert response.status_code == 404


def test_create_payment(client, sample_invoice):
    """Test creating a payment via API"""
    payment_data = {
        "amount": "500.00"
    }
    
    response = client.post(f"/invoices/{sample_invoice.id}/payments", json=payment_data)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "500.00"
    assert data["invoice_id"] == sample_invoice.id


def test_create_payment_overpayment_rejected(client, sample_invoice):
    """Test that API rejects overpayment"""
    payment_data = {
        "amount": "2000.00"  # More than invoice amount
    }
    
    response = client.post(f"/invoices/{sample_invoice.id}/payments", json=payment_data)
    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()


def test_list_invoices(client, sample_invoice):
    """Test listing all invoices"""
    response = client.get("/invoices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_invoices_filter_by_status(client, sample_invoice):
    """Test filtering invoices by status"""
    response = client.get("/invoices?status=PENDING")
    assert response.status_code == 200
    data = response.json()
    assert all(inv["status"] == "PENDING" for inv in data)