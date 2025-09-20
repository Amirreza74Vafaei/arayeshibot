from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.admin_panel import schemas, security
from src.db import crud, session as db_session

router = APIRouter()

@router.post("/", response_model=schemas.Coupon)
def create_coupon(
    coupon: schemas.CouponCreate,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Create a new coupon.
    """
    existing_coupon = crud.get_coupon_by_code(db, code=coupon.code)
    if existing_coupon:
        raise HTTPException(status_code=400, detail="Coupon with this code already exists.")
    return crud.create_coupon(db=db, coupon=coupon)

@router.get("/{code}", response_model=schemas.Coupon)
def read_coupon(
    code: str,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Retrieve a coupon by its code.
    """
    db_coupon = crud.get_coupon_by_code(db, code=code)
    if db_coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return db_coupon
