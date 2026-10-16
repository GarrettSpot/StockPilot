from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from .models import Product
from .schemas import ProductCreate, ProductOut, ProductUpdate, StatsOut


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Production containers run Alembic before Uvicorn; create_all keeps tests self-contained.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/")
def root():
    return {"service": settings.app_name, "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(select(Product.id).limit(1))
    return {"status": "READY"}


@app.get("/api/products/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    products = list(db.scalars(select(Product)))
    total = len(products)
    out_of_stock = sum(1 for p in products if p.quantity <= 0)
    low_stock = sum(1 for p in products if 0 < p.quantity <= p.reorder_level)
    in_stock = total - out_of_stock - low_stock
    value = sum(float(p.price) * p.quantity for p in products)
    return StatsOut(
        total=total,
        inStock=in_stock,
        lowStock=low_stock,
        outOfStock=out_of_stock,
        inventoryValue=round(value, 2),
    )


@app.get("/api/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return list(db.scalars(select(Product).order_by(Product.id.desc())))


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Product).where(Product.sku == payload.sku))
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/api/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
