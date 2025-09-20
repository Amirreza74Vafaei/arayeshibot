from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.admin_panel import schemas, security
from src.db import crud, session as db_session

router = APIRouter()

@router.post("/", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Create a new category.
    """
    return crud.create_category(db=db, category=category)

@router.get("/", response_model=List[schemas.Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Retrieve all categories.
    """
    categories = crud.get_all_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=schemas.Category)
def read_category(
    category_id: int,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Retrieve a single category by its ID.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# Note: Update and Delete for categories are not implemented yet.
# This can be added if required, but for now, we have the core functionality.
