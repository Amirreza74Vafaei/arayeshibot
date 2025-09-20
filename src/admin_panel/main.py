from fastapi import FastAPI

app = FastAPI(
    title="Telegram Shop Admin Panel API",
    description="API for managing the Telegram shop bot.",
    version="0.1.0"
)

from src.admin_panel.api.endpoints import login
from src.admin_panel import schemas, security
from fastapi import Depends

from src.admin_panel.api.endpoints import products

from src.admin_panel.api.endpoints import categories

from src.admin_panel.api.endpoints import orders

from src.admin_panel.api.endpoints import coupons

from src.admin_panel.api.endpoints import reports

# Mount the login router
app.include_router(login.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(coupons.router, prefix="/api/v1/coupons", tags=["Coupons"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/")
async def root():
    """
    Root endpoint for the admin panel.
    Provides a simple welcome message.
    """
    return {"message": "Welcome to the Telegram Shop Admin Panel"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

# Example of a protected endpoint
@app.get("/users/me", response_model=schemas.AdminUserBase)
async def read_users_me(current_user: dict = Depends(security.get_current_admin_user)):
    # In a real app, you would fetch the full user object from the DB
    # For now, we return a mock response based on the token's username
    return {"name": current_user.get("username"), "role": "admin"}
