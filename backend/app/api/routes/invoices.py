from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.invoice import InvoiceStatus
from app.api.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.api.schemas.payment import PaymentCreate, PaymentResponse
from app.api.services.invoice_service import (
    create_invoice,
    get_invoice,
    get_all_invoices,
    post_invoice,
    void_invoice,
)
from app.api.services.invoice_service import InvoiceError
from app.api.services.payment_service import record_payment, PaymentError

router = APIRouter(prefix="/invoices", tags=["invoices"])


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=InvoiceResponse, status_code=201)
def create_invoice_endpoint(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db)
):
    """Create a new invoice"""
    try:
        invoice = create_invoice(db, invoice_data)
        return invoice
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get invoice details including payments"""
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    return invoice

@router.post("/{invoice_id}/post", response_model=InvoiceResponse)
def post_invoice_endpoint(invoice_id: int, db: Session = Depends(get_db)):
    """Send invoice for payment (DRAFT → PENDING)."""
    try:
        invoice = post_invoice(db, invoice_id)
        return invoice
    except InvoiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{invoice_id}/void", response_model=InvoiceResponse)
def void_invoice_endpoint(invoice_id: int, db: Session = Depends(get_db)):
    """Cancel invoice (set status to VOID)."""
    try:
        invoice = void_invoice(db, invoice_id)
        return invoice
    except InvoiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{invoice_id}/payments", response_model=PaymentResponse, status_code=201)
def create_payment_endpoint(
    invoice_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
):
    """Record a payment against an invoice"""
    try:
        payment = record_payment(db, invoice_id, payment_data)
        return payment
    except PaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=list[InvoiceResponse])
def list_invoices_endpoint(
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Filter invoices issued from this date"),
    to_date: Optional[datetime] = Query(None, alias="to", description="Filter invoices issued to this date"),
    db: Session = Depends(get_db)
):
    """List all invoices with optional filters"""
    invoices = get_all_invoices(
        db,
        status=status,
        customer_id=customer_id,
        from_date=from_date,
        to_date=to_date
    )
    return invoices