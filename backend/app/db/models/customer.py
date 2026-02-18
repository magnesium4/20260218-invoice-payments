from __future__ import annotations

from sqlalchemy import String, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # One customer -> many invoices
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )