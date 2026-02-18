from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.models.invoice import Invoice, InvoiceStatus
from app.db.models.payment import Payment
from app.api.schemas.payment import PaymentCreate


class PaymentError(Exception):
    """Custom exception for payment-related errors"""
    pass


def calculate_total_paid(db: Session, invoice_id: int) -> Decimal:
    """Calculate the total amount paid for an invoice"""
    result = db.scalar(
        select(func.sum(Payment.amount))
        .where(Payment.invoice_id == invoice_id)
    )
    return Decimal(result or 0)


def record_payment(
    db: Session, 
    invoice_id: int, 
    payment_data: PaymentCreate
) -> Payment:
    """
    Record a payment against an invoice.
    Enforces business rules:
    - Payment must be positive
    - No overpayment
    - Cannot pay VOID or PAID invoices
    """
    # Get invoice with lock to prevent concurrent payment issues
    invoice = db.scalar(
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .with_for_update()  # Row-level lock for concurrency
    )
    
    if not invoice:
        raise PaymentError(f"Invoice {invoice_id} not found")
    
    # Business rule: Drafts cannot accept payments before being posted
    if invoice.status == InvoiceStatus.DRAFT:
        raise PaymentError(
            "Drafts cannot accept payments before being posted."
        )

    # Business rule: Cannot pay VOID or PAID invoices
    if invoice.status in (InvoiceStatus.VOID, InvoiceStatus.PAID):
        raise PaymentError(
            f"Cannot record payment for invoice with status {invoice.status.value}"
        )
    
    # Calculate current total paid
    total_paid = calculate_total_paid(db, invoice_id)
    new_payment_amount = Decimal(str(payment_data.amount))
    
    # Business rule: Payment must be positive (enforced by Pydantic, but double-check)
    if new_payment_amount <= 0:
        raise PaymentError("Payment amount must be positive")
    
    # Business rule: No overpayment
    remaining_balance = Decimal(str(invoice.amount)) - total_paid
    if new_payment_amount > remaining_balance:
        raise PaymentError(
            f"Payment amount {new_payment_amount} exceeds remaining balance {remaining_balance}"
        )
    
    # Create payment
    paid_at = payment_data.paid_at or datetime.now(timezone.utc)
    payment = Payment(
        invoice_id=invoice_id,
        amount=new_payment_amount,
        paid_at=paid_at
    )
    db.add(payment)

    # Business rule: Update invoice status to PAID if fully paid
    new_total_paid = total_paid + new_payment_amount
    if new_total_paid >= Decimal(str(invoice.amount)):
        invoice.status = InvoiceStatus.PAID
    
    db.commit()
    db.refresh(payment)
    
    return payment