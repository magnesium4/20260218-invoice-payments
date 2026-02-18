from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationship
    invoice: Mapped["Invoice"] = relationship(back_populates="payments")