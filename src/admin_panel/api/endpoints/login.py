from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.admin_panel import schemas, security
from src.db import crud, session as db_session

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(db_session.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticates an admin user and returns a JWT access token.
    """
    admin_user = crud.get_admin_user_by_name(db, name=form_data.username)
    if not admin_user or not security.verify_password(form_data.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": admin_user.name}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
