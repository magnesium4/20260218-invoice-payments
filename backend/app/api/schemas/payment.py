from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0, description="Payment amount must be positive")
    paid_at: Optional[datetime] = None  # If None, use current time


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: Decimal
    paid_at: datetime
    
    model_config = ConfigDict(from_attributes=True)