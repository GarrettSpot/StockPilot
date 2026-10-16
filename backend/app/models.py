from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="General")
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=10)
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    supplier: Mapped[str] = mapped_column(String(120), default="Unassigned")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    @property
    def status(self) -> str:
        if self.quantity <= 0:
            return "OUT_OF_STOCK"
        if self.quantity <= self.reorder_level:
            return "LOW_STOCK"
        return "IN_STOCK"
