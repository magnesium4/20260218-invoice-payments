import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.api.services.payment_service import record_payment, PaymentError, calculate_total_paid
from app.api.schemas.payment import PaymentCreate
from app.db.models.invoice import InvoiceStatus


def test_calculate_total_paid_empty(db_session, sample_invoice):
    """Test calculating total paid when no payments exist"""
    total = calculate_total_paid(db_session, sample_invoice.id)
    assert total == Decimal("0")


def test_record_payment_success(db_session, sample_invoice):
    """Test successfully recording a payment"""
    payment_data = PaymentCreate(amount=Decimal("500.00"))
    payment = record_payment(db_session, sample_invoice.id, payment_data)
    
    assert payment.id is not None
    assert payment.amount == Decimal("500.00")
    assert payment.invoice_id == sample_invoice.id
    assert payment.paid_at is not None


def test_record_payment_updates_invoice_status_to_paid(db_session, sample_invoice):
    """Test that invoice status changes to PAID when fully paid"""
    # Pay the full amount
    payment_data = PaymentCreate(amount=Decimal("1000.00"))
    record_payment(db_session, sample_invoice.id, payment_data)
    
    db_session.refresh(sample_invoice)
    assert sample_invoice.status == InvoiceStatus.PAID


def test_record_payment_partial_payment(db_session, sample_invoice):
    """Test that partial payment doesn't change status to PAID"""
    payment_data = PaymentCreate(amount=Decimal("500.00"))
    record_payment(db_session, sample_invoice.id, payment_data)
    
    db_session.refresh(sample_invoice)
    assert sample_invoice.status == InvoiceStatus.PENDING


def test_record_payment_rejects_overpayment(db_session, sample_invoice):
    """Test that overpayment is rejected"""
    payment_data = PaymentCreate(amount=Decimal("1500.00"))
    
    with pytest.raises(PaymentError) as exc_info:
        record_payment(db_session, sample_invoice.id, payment_data)
    
    assert "exceeds remaining balance" in str(exc_info.value).lower()


def test_record_payment_rejects_negative_amount(db_session, sample_invoice):
    """Test that negative payment amount is rejected by Pydantic validation"""
    with pytest.raises(ValidationError) as exc_info:
        PaymentCreate(amount=Decimal("-100.00"))
    
    assert "greater than 0" in str(exc_info.value).lower()


def test_record_payment_rejects_zero_amount(db_session, sample_invoice):
    """Test that zero payment amount is rejected by Pydantic validation"""
    with pytest.raises(ValidationError) as exc_info:
        PaymentCreate(amount=Decimal("0.00"))
    
    assert "greater than 0" in str(exc_info.value).lower()


def test_record_payment_rejects_paid_invoice(db_session, sample_customer):
    """Test that payment to PAID invoice is rejected"""
    from app.db.models.invoice import Invoice
    from datetime import datetime, timezone
    
    # Create a paid invoice
    paid_invoice = Invoice(
        customer_id=sample_customer.id,
        amount=1000.00,
        currency="USD",
        issued_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc),
        status=InvoiceStatus.PAID
    )
    db_session.add(paid_invoice)
    db_session.commit()
    db_session.refresh(paid_invoice)
    
    payment_data = PaymentCreate(amount=Decimal("100.00"))
    
    with pytest.raises(PaymentError) as exc_info:
        record_payment(db_session, paid_invoice.id, payment_data)
    
    assert "paid" in str(exc_info.value).lower()


def test_record_payment_rejects_void_invoice(db_session, sample_customer):
    """Test that payment to VOID invoice is rejected"""
    from app.db.models.invoice import Invoice
    from datetime import datetime, timezone
    
    void_invoice = Invoice(
        customer_id=sample_customer.id,
        amount=1000.00,
        currency="USD",
        issued_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc),
        status=InvoiceStatus.VOID
    )
    db_session.add(void_invoice)
    db_session.commit()
    db_session.refresh(void_invoice)
    
    payment_data = PaymentCreate(amount=Decimal("100.00"))
    
    with pytest.raises(PaymentError) as exc_info:
        record_payment(db_session, void_invoice.id, payment_data)
    
    assert "void" in str(exc_info.value).lower()


def test_record_payment_multiple_partial_payments(db_session, sample_invoice):
    """Test multiple partial payments that sum to full amount"""
    # First payment
    payment1 = PaymentCreate(amount=Decimal("300.00"))
    record_payment(db_session, sample_invoice.id, payment1)
    
    # Second payment
    payment2 = PaymentCreate(amount=Decimal("400.00"))
    record_payment(db_session, sample_invoice.id, payment2)
    
    # Third payment - should complete and mark as PAID
    payment3 = PaymentCreate(amount=Decimal("300.00"))
    record_payment(db_session, sample_invoice.id, payment3)
    
    db_session.refresh(sample_invoice)
    assert sample_invoice.status == InvoiceStatus.PAID
    
    total = calculate_total_paid(db_session, sample_invoice.id)
    assert total == Decimal("1000.00")