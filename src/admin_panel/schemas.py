from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Admin User Schemas ---
class AdminUserBase(BaseModel):
    name: str
    telegram_id: Optional[int] = None
    role: str = "admin"

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUser(AdminUserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# --- Order Schemas ---
class OrderItem(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: Decimal

    class Config:
        from_attributes = True

class Order(BaseModel):
    id: int
    user_id: int
    total: Decimal
    status: str
    payment_method: str
    payment_status: str
    address: dict
    shipping_cost: Decimal
    created_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None


# --- Coupon Schemas ---
class CouponBase(BaseModel):
    code: str
    discount_type: str # 'percent' or 'fixed'
    value: Decimal
    expires_at: Optional[datetime] = None
    usage_limit: int = 1
    is_active: bool = True

class CouponCreate(CouponBase):
    pass

class Coupon(CouponBase):
    id: int
    usage_count: int

    class Config:
        from_attributes = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    title: str
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    sku: str
    title: str
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    discount_price: Optional[Decimal] = Field(None, gt=0)
    stock: int = 0
    category_id: int
    weight: Optional[Decimal] = None
    images: Optional[List[str]] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    category: Category # Nested schema

    class Config:
        orm_mode = True
