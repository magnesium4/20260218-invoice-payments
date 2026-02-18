from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models.invoice import Invoice, InvoiceStatus
from app.api.schemas.invoice import InvoiceCreate


def create_invoice(db: Session, invoice_data: InvoiceCreate) -> Invoice:
    """Create a new invoice"""
    invoice = Invoice(**invoice_data.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice(db: Session, invoice_id: int) -> Optional[Invoice]:
    """Get invoice by ID with payments loaded"""
    return db.scalar(
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(selectinload(Invoice.payments))
    )

class InvoiceError(Exception):
    """Invoice operation error"""
    pass


def post_invoice(db: Session, invoice_id: int) -> Invoice:
    """Send invoice for payment: DRAFT → PENDING."""
    invoice = db.scalar(
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(selectinload(Invoice.payments))
    )
    if not invoice:
        raise InvoiceError(f"Invoice {invoice_id} not found")
    if invoice.status != InvoiceStatus.DRAFT:
        raise InvoiceError(f"Invoice must be DRAFT to post (current: {invoice.status.value})")
    invoice.status = InvoiceStatus.PENDING
    db.commit()
    db.refresh(invoice)
    return invoice


def void_invoice(db: Session, invoice_id: int) -> Invoice:
    """Cancel invoice: set status to VOID (only DRAFT or PENDING)."""
    invoice = db.scalar(
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(selectinload(Invoice.payments))
    )
    if not invoice:
        raise InvoiceError(f"Invoice {invoice_id} not found")
    if invoice.status == InvoiceStatus.PAID:
        raise InvoiceError("Cannot void a paid invoice")
    if invoice.status == InvoiceStatus.VOID:
        raise InvoiceError("Invoice is already void")
    invoice.status = InvoiceStatus.VOID
    db.commit()
    db.refresh(invoice)
    return invoice


def get_customer_invoices(
    db: Session,
    customer_id: int,
    status: Optional[InvoiceStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> list[Invoice]:
    """Get invoices for a customer with optional filters"""
    query = select(Invoice).where(Invoice.customer_id == customer_id)
    
    if status:
        query = query.where(Invoice.status == status)
    
    if from_date:
        query = query.where(Invoice.issued_at >= from_date)
    
    if to_date:
        query = query.where(Invoice.issued_at <= to_date)
    
    query = query.options(selectinload(Invoice.payments)) 
    query = query.order_by(Invoice.issued_at.desc())
    
    return list(db.scalars(query).all())


def get_all_invoices(
    db: Session,
    status: Optional[InvoiceStatus] = None,
    customer_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> list[Invoice]:
    """Get all invoices with optional filters"""
    query = select(Invoice)
    
    if status:
        query = query.where(Invoice.status == status)
    
    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)
    
    if from_date:
        query = query.where(Invoice.issued_at >= from_date)
    
    if to_date:
        query = query.where(Invoice.issued_at <= to_date)
    
    query = query.options(selectinload(Invoice.payments))
    query = query.order_by(Invoice.issued_at.desc())
    
    return list(db.scalars(query).all())