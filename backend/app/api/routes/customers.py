from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.customer import Customer
from app.db.models.invoice import InvoiceStatus
from app.api.schemas.customer import CustomerCreate, CustomerResponse
from app.api.schemas.invoice import InvoiceResponse
from app.api.services.invoice_service import get_customer_invoices

router = APIRouter(prefix="/customers", tags=["customers"])


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer_endpoint(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """Create a new customer"""
    try:
        customer = Customer(name=customer_data.name)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[CustomerResponse])
def list_customers_endpoint(
    db: Session = Depends(get_db)
):
    """List all customers"""
    customers = db.query(Customer).order_by(Customer.id).all()
    return customers


@router.get("/{customer_id}/invoices", response_model=list[InvoiceResponse])
def get_customer_invoices_endpoint(
    customer_id: int,
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Filter invoices issued from this date"),
    to_date: Optional[datetime] = Query(None, alias="to", description="Filter invoices issued to this date"),
    db: Session = Depends(get_db)
):
    """List invoices for a customer with optional filters"""
    invoices = get_customer_invoices(
        db, 
        customer_id, 
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    return invoices