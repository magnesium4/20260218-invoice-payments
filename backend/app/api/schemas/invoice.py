from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.db.models.invoice import InvoiceStatus


class InvoiceBase(BaseModel):
    customer_id: int
    amount: Decimal = Field(gt=0, description="Invoice amount must be positive")
    currency: str = Field(min_length=3, max_length=3)
    issued_at: datetime
    due_at: datetime
    status: InvoiceStatus = InvoiceStatus.DRAFT


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: Decimal
    paid_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InvoiceResponse(InvoiceBase):
    id: int
    customer_id: int
    amount: Decimal
    currency: str
    issued_at: datetime
    due_at: datetime
    status: InvoiceStatus
    payments: list[PaymentResponse] = []
    
    model_config = ConfigDict(from_attributes=True)