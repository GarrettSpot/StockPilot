from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ProductStatus = Literal["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"]


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=60)
    category: str = "General"
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    price: float = Field(default=0, ge=0)
    supplier: str = "Unassigned"


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    sku: str | None = Field(default=None, min_length=1, max_length=60)
    category: str | None = None
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    price: float | None = Field(default=None, ge=0)
    supplier: str | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    quantity: int
    reorder_level: int
    price: float
    supplier: str
    status: ProductStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StatsOut(BaseModel):
    total: int
    inStock: int
    lowStock: int
    outOfStock: int
    inventoryValue: float
