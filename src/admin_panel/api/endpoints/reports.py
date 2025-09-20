from datetime import datetime, date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.admin_panel import security
from src.db import crud, session as db_session

router = APIRouter()

@router.get("/sales")
def get_sales_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(db_session.get_db),
    current_user: dict = Depends(security.get_current_admin_user)
):
    """
    Get a sales report for a given date range.
    The report includes total orders and total revenue for non-canceled orders.
    """
    # Convert date to datetime for the query
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    report_data = crud.get_sales_report(db, start_date=start_datetime, end_date=end_datetime)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "report": report_data
    }
