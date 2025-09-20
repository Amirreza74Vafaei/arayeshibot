import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Add project root to path to allow imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.models import Base, Coupon, DiscountType
from src.db import crud

# Setup for in-memory SQLite database for testing
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

# --- Test Cases for coupon validation ---

def test_validate_valid_coupon(db_session):
    """Tests that a normal, valid coupon passes validation."""
    valid_coupon = Coupon(
        code="VALID10", discount_type=DiscountType.PERCENT, value=10,
        usage_limit=10, usage_count=5, is_active=True
    )
    db_session.add(valid_coupon)
    db_session.commit()

    result = crud.validate_coupon(db_session, "VALID10")
    assert result is not None
    assert result.code == "VALID10"

def test_validate_nonexistent_coupon(db_session):
    """Tests that a non-existent coupon fails validation."""
    result = crud.validate_coupon(db_session, "FAKECODE")
    assert result is None

def test_validate_inactive_coupon(db_session):
    """Tests that an inactive coupon fails validation."""
    inactive_coupon = Coupon(
        code="INACTIVE", discount_type=DiscountType.FIXED, value=5000,
        usage_limit=10, usage_count=0, is_active=False
    )
    db_session.add(inactive_coupon)
    db_session.commit()

    result = crud.validate_coupon(db_session, "INACTIVE")
    assert result is None

from datetime import timezone

def test_validate_expired_coupon(db_session):
    """Tests that an expired coupon fails validation."""
    expired_coupon = Coupon(
        code="EXPIRED", discount_type=DiscountType.PERCENT, value=15,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        usage_limit=10, usage_count=0, is_active=True
    )
    db_session.add(expired_coupon)
    db_session.commit()

    result = crud.validate_coupon(db_session, "EXPIRED")
    assert result is None

def test_validate_usage_limit_reached_coupon(db_session):
    """Tests that a coupon with usage limit reached fails validation."""
    limit_reached_coupon = Coupon(
        code="LIMITOUT", discount_type=DiscountType.FIXED, value=10000,
        usage_limit=5, usage_count=5, is_active=True
    )
    db_session.add(limit_reached_coupon)
    db_session.commit()

    result = crud.validate_coupon(db_session, "LIMITOUT")
    assert result is None
