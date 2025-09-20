from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.admin_panel import schemas, security
from src.db import crud, session as db_session
from src.db import models

router = APIRouter()

@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Create a new product.
    """
    return crud.create_product(db=db, product=product)

@router.get("/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Retrieve all products.
    """
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(
    product_id: int,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Retrieve a single product by its ID.
    """
    db_product = crud.get_product_by_id(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Update an existing product.
    """
    db_product = crud.update_product(db, product_id=product_id, product_in=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(
    product_id: int,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Delete a product.
    """
    db_product = crud.delete_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product
