from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Numeric,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PAID = "PAID"
    VOID = "VOID"


class Invoice(Base):
    __tablename__ = "invoices"

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_invoices_amount_positive"),
        CheckConstraint("currency <> ''", name="ck_invoices_currency_nonempty"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status"),
        nullable=False,
        default=InvoiceStatus.DRAFT,
        index=True,
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="invoices")

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Payment.paid_at",
    )