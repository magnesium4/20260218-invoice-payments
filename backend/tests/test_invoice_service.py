import pytest
from datetime import datetime, timezone

from app.api.services.invoice_service import (
    create_invoice,
    get_invoice,
    get_all_invoices,
    post_invoice,
    void_invoice,
    InvoiceError,
)
from app.api.schemas.invoice import InvoiceCreate
from app.db.models.invoice import InvoiceStatus


def test_create_invoice(db_session, sample_customer):
    """Test creating an invoice via service"""
    data = InvoiceCreate(
        customer_id=sample_customer.id,
        amount="250.50",
        currency="GBP",
        issued_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc),
        status=InvoiceStatus.DRAFT,
    )
    invoice = create_invoice(db_session, data)
    assert invoice.id is not None
    assert invoice.amount == 250.50
    assert invoice.currency == "GBP"
    assert invoice.status == InvoiceStatus.DRAFT


def test_get_invoice(db_session, sample_invoice):
    """Test getting an invoice by ID"""
    inv = get_invoice(db_session, sample_invoice.id)
    assert inv is not None
    assert inv.id == sample_invoice.id
    assert inv.amount == sample_invoice.amount


def test_get_invoice_not_found(db_session):
    """Test get_invoice returns None for missing ID"""
    assert get_invoice(db_session, 99999) is None


def test_post_invoice_success(db_session, sample_draft_invoice):
    """Test post_invoice changes DRAFT to PENDING"""
    result = post_invoice(db_session, sample_draft_invoice.id)
    assert result.status == InvoiceStatus.PENDING
    db_session.refresh(sample_draft_invoice)
    assert sample_draft_invoice.status == InvoiceStatus.PENDING


def test_post_invoice_not_found(db_session):
    """Test post_invoice raises for missing invoice"""
    with pytest.raises(InvoiceError) as exc_info:
        post_invoice(db_session, 99999)
    assert "not found" in str(exc_info.value).lower()


def test_post_invoice_not_draft(db_session, sample_invoice):
    """Test post_invoice raises when invoice is not DRAFT"""
    with pytest.raises(InvoiceError) as exc_info:
        post_invoice(db_session, sample_invoice.id)
    assert "draft" in str(exc_info.value).lower()


def test_void_invoice_success(db_session, sample_invoice):
    """Test void_invoice sets status to VOID"""
    result = void_invoice(db_session, sample_invoice.id)
    assert result.status == InvoiceStatus.VOID
    db_session.refresh(sample_invoice)
    assert sample_invoice.status == InvoiceStatus.VOID


def test_void_invoice_not_found(db_session):
    """Test void_invoice raises for missing invoice"""
    with pytest.raises(InvoiceError) as exc_info:
        void_invoice(db_session, 99999)
    assert "not found" in str(exc_info.value).lower()


def test_void_invoice_paid_rejected(db_session, sample_customer):
    """Test void_invoice raises for PAID invoice"""
    from app.db.models.invoice import Invoice
    paid = Invoice(
        customer_id=sample_customer.id,
        amount=100.00,
        currency="USD",
        issued_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc),
        status=InvoiceStatus.PAID,
    )
    db_session.add(paid)
    db_session.commit()
    db_session.refresh(paid)
    with pytest.raises(InvoiceError) as exc_info:
        void_invoice(db_session, paid.id)
    assert "paid" in str(exc_info.value).lower()


def test_void_invoice_already_void(db_session, sample_invoice):
    """Test void_invoice raises when already VOID"""
    void_invoice(db_session, sample_invoice.id)
    with pytest.raises(InvoiceError) as exc_info:
        void_invoice(db_session, sample_invoice.id)
    assert "void" in str(exc_info.value).lower()


def test_get_all_invoices_filter_by_status(db_session, sample_invoice):
    """Test get_all_invoices filters by status"""
    result = get_all_invoices(db_session, status=InvoiceStatus.PENDING)
    assert all(inv.status == InvoiceStatus.PENDING for inv in result)


def test_get_all_invoices_filter_by_customer(db_session, sample_invoice, sample_customer):
    """Test get_all_invoices filters by customer_id"""
    result = get_all_invoices(db_session, customer_id=sample_customer.id)
    assert all(inv.customer_id == sample_customer.id for inv in result)


def test_get_all_invoices_filter_by_dates(db_session, sample_invoice):
    """Test get_all_invoices filters by from_date and to_date"""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    from_date = now - timedelta(days=30)
    to_date = now + timedelta(days=1)
    result = get_all_invoices(db_session, from_date=from_date, to_date=to_date)
    assert isinstance(result, list)
    # sample_invoice was created with issued_at=now, so it should be in range
    ids = [inv.id for inv in result]
    assert sample_invoice.id in ids
