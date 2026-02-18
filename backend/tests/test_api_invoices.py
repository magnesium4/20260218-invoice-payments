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


def test_create_invoice_validation_invalid_currency(client, sample_customer):
    """Test that invalid currency (not 3 chars) returns 422"""
    from datetime import datetime, timezone
    invoice_data = {
        "customer_id": sample_customer.id,
        "amount": "100.00",
        "currency": "US",  # invalid: must be 3 chars
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "due_at": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/invoices", json=invoice_data)
    assert response.status_code == 422


def test_create_invoice_validation_negative_amount(client, sample_customer):
    """Test that negative amount returns 422"""
    from datetime import datetime, timezone
    invoice_data = {
        "customer_id": sample_customer.id,
        "amount": "-10.00",
        "currency": "USD",
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "due_at": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/invoices", json=invoice_data)
    assert response.status_code == 422


def test_get_invoice_invalid_id(client):
    """Test getting invoice with non-integer ID returns 422"""
    response = client.get("/invoices/abc")
    assert response.status_code == 422


def test_post_invoice_success(client, sample_draft_invoice):
    """Test posting a DRAFT invoice changes status to PENDING"""
    response = client.post(f"/invoices/{sample_draft_invoice.id}/post")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"
    assert data["id"] == sample_draft_invoice.id


def test_post_invoice_not_found(client):
    """Test posting non-existent invoice returns 400"""
    response = client.post("/invoices/99999/post")
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


def test_post_invoice_not_draft(client, sample_invoice):
    """Test posting a non-DRAFT invoice returns 400"""
    response = client.post(f"/invoices/{sample_invoice.id}/post")
    assert response.status_code == 400
    assert "draft" in response.json()["detail"].lower()


def test_void_invoice_success(client, sample_invoice):
    """Test voiding a PENDING invoice"""
    response = client.post(f"/invoices/{sample_invoice.id}/void")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VOID"


def test_void_invoice_paid_rejected(client, sample_invoice):
    """Test voiding a PAID invoice returns 400"""
    # First pay the invoice in full
    client.post(f"/invoices/{sample_invoice.id}/payments", json={"amount": "1000.00"})
    response = client.post(f"/invoices/{sample_invoice.id}/void")
    assert response.status_code == 400
    assert "paid" in response.json()["detail"].lower()


def test_void_invoice_already_void(client, sample_invoice):
    """Test voiding an already VOID invoice returns 400"""
    client.post(f"/invoices/{sample_invoice.id}/void")
    response = client.post(f"/invoices/{sample_invoice.id}/void")
    assert response.status_code == 400
    assert "void" in response.json()["detail"].lower()


def test_void_invoice_draft_rejected(client, sample_draft_invoice):
    """Test voiding a DRAFT invoice returns 400 (drafts must be deleted, not voided)"""
    response = client.post(f"/invoices/{sample_draft_invoice.id}/void")
    assert response.status_code == 400
    assert "draft" in response.json()["detail"].lower()


def test_delete_invoice_success(client, sample_draft_invoice):
    """Test deleting a DRAFT invoice returns 204 and removes it from DB"""
    response = client.delete(f"/invoices/{sample_draft_invoice.id}")
    assert response.status_code == 204
    get_response = client.get(f"/invoices/{sample_draft_invoice.id}")
    assert get_response.status_code == 404


def test_delete_invoice_pending_rejected(client, sample_invoice):
    """Test deleting a PENDING invoice returns 400"""
    response = client.delete(f"/invoices/{sample_invoice.id}")
    assert response.status_code == 400
    assert "draft" in response.json()["detail"].lower()


def test_list_invoices_filter_by_customer(client, sample_invoice, sample_customer):
    """Test filtering invoices by customer_id"""
    response = client.get(f"/invoices?customer_id={sample_customer.id}")
    assert response.status_code == 200
    data = response.json()
    assert all(inv["customer_id"] == sample_customer.id for inv in data)


def test_list_invoices_filter_by_dates(client, sample_invoice):
    """Test filtering invoices by from and to date"""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    from_str = (now.replace(day=1)).isoformat().replace("+00:00", "Z")
    to_str = now.isoformat().replace("+00:00", "Z")
    response = client.get(f"/invoices?from={from_str}&to={to_str}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_payment_on_draft_rejected(client, sample_draft_invoice):
    """Test that payment on DRAFT invoice is rejected"""
    response = client.post(
        f"/invoices/{sample_draft_invoice.id}/payments",
        json={"amount": "100.00"}
    )
    assert response.status_code == 400
    assert "draft" in response.json()["detail"].lower()


def test_create_payment_invalid_amount(client, sample_invoice):
    """Test that payment with missing/invalid amount returns 422"""
    response = client.post(
        f"/invoices/{sample_invoice.id}/payments",
        json={"amount": "-50.00"}
    )
    assert response.status_code == 422


def test_create_payment_not_found(client, sample_customer):
    """Test payment on non-existent invoice returns 400"""
    response = client.post(
        "/invoices/99999/payments",
        json={"amount": "100.00"}
    )
    assert response.status_code == 400