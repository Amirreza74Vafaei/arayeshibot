from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.admin_panel import schemas, security
from src.db import crud, session as db_session

router = APIRouter()

@router.get("/", response_model=List[schemas.Order])
def read_orders(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Retrieve all orders, with optional filtering by status.
    """
    orders = crud.get_all_orders(db, skip=skip, limit=limit, status=status)
    return orders

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(
    order_id: int,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Retrieve a single order by its ID.
    """
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.put("/{order_id}", response_model=schemas.Order)
def update_order(
    order_id: int,
    order: schemas.OrderUpdate,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Update an order's status or payment status.
    """
    db_order = crud.update_order(db, order_id=order_id, order_in=order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order
