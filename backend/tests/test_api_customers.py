import pytest
from datetime import datetime, timezone


def test_create_customer(client):
    """Test creating a new customer via API"""
    response = client.post("/customers", json={"name": "Acme Corp"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert "id" in data


def test_list_customers(client, sample_customer):
    """Test listing all customers"""
    response = client.get("/customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    names = [c["name"] for c in data]
    assert sample_customer.name in names


def test_list_customers_empty(client):
    """Test listing customers when none exist (empty list)"""
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json() == []


def test_create_customer_validation_empty_name(client):
    """Test that empty customer name returns 422"""
    response = client.post("/customers", json={"name": ""})
    assert response.status_code == 422


def test_create_customer_validation_name_too_long(client):
    """Test that customer name over 255 chars returns 422"""
    response = client.post("/customers", json={"name": "x" * 256})
    assert response.status_code == 422


def test_get_customer_invoices(client, sample_customer, sample_invoice):
    """Test listing invoices for a customer"""
    response = client.get(f"/customers/{sample_customer.id}/invoices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(inv["customer_id"] == sample_customer.id for inv in data)


def test_get_customer_invoices_filter_by_status(client, sample_customer, sample_invoice):
    """Test filtering customer invoices by status"""
    response = client.get(f"/customers/{sample_customer.id}/invoices?status=PENDING")
    assert response.status_code == 200
    data = response.json()
    assert all(inv["status"] == "PENDING" for inv in data)


def test_get_customer_invoices_nonexistent_returns_empty(client):
    """Test customer invoices for non-existent customer returns empty list"""
    response = client.get("/customers/99999/invoices")
    assert response.status_code == 200
    assert response.json() == []
