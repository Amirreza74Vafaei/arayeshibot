from sqlalchemy.orm import Session
from . import models, session as db_session
from aiogram import types

def get_or_create_user(db: Session, telegram_user: types.User) -> models.User:
    """
    Retrieves a user by their Telegram ID or creates a new one if they don't exist.
    """
    # Attempt to find the user by their telegram_id
    user = db.query(models.User).filter(models.User.telegram_id == telegram_user.id).first()

    if user:
        # User exists, update their details if they've changed
        update_data = {
            'username': telegram_user.username,
            'first_name': telegram_user.first_name,
            'last_name': telegram_user.last_name,
        }
        # Filter out None values so we don't overwrite existing data with nothing
        update_data = {k: v for k, v in update_data.items() if v is not None}

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
    else:
        # User does not exist, create a new one
        user = models.User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

def get_categories(db: Session) -> list[models.Category]:
    """
    Retrieves all product categories from the database.
    """
    return db.query(models.Category).order_by(models.Category.id).all()


def get_products_by_category(db: Session, category_id: int, page: int = 1, page_size: int = 6) -> list[models.Product]:
    """
    Retrieves a paginated list of products for a given category.
    """
    offset = (page - 1) * page_size
    return db.query(models.Product).filter(models.Product.category_id == category_id).offset(offset).limit(page_size).all()


def count_products_by_category(db: Session, category_id: int) -> int:
    """
    Counts the total number of products in a given category.
    """
    return db.query(models.Product).filter(models.Product.category_id == category_id).count()


def get_product_by_id(db: Session, product_id: int) -> models.Product | None:
    """
    Retrieves a single product by its ID.
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_or_create_cart(db: Session, user_id: int) -> models.Cart:
    """
    Retrieves a user's cart or creates a new one if it doesn't exist.
    """
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        cart = models.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def add_item_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1) -> models.CartItem:
    """
    Adds a product to the user's cart. If the item already exists, it increments the quantity.
    """
    cart = get_or_create_cart(db, user_id)
    product = get_product_by_id(db, product_id)

    if not product:
        raise ValueError("Product not found")

    # Check if the item is already in the cart
    cart_item = db.query(models.CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()

    if cart_item:
        # Item exists, update quantity
        cart_item.quantity += quantity
    else:
        # Item does not exist, create a new one
        cart_item = models.CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=product.discount_price if product.discount_price else product.price
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


from sqlalchemy.orm import joinedload

def get_cart_items(db: Session, user_id: int) -> list[models.CartItem]:
    """
    Retrieves all items in a user's cart, with product details.
    Uses joinedload to prevent the N+1 query problem.
    """
    cart = get_or_create_cart(db, user_id)
    if not cart:
        return []

    return (
        db.query(models.CartItem)
        .options(joinedload(models.CartItem.product))
        .filter(models.CartItem.cart_id == cart.id)
        .all()
    )


def create_order_from_cart(db: Session, user_id: int, address_data: dict, coupon: models.Coupon = None) -> models.Order:
    """
    Creates a new order from the user's cart, applying a coupon if provided, then clears the cart.
    """
    cart_items = get_cart_items(db, user_id)
    if not cart_items:
        raise ValueError("Cannot create an order from an empty cart.")

    # Calculate total and discount
    subtotal = sum(item.quantity * item.unit_price for item in cart_items)
    discount_amount = 0
    final_total = subtotal
    coupon_code = None

    if coupon:
        if coupon.discount_type == models.DiscountType.FIXED:
            discount_amount = min(coupon.value, subtotal)
        elif coupon.discount_type == models.DiscountType.PERCENT:
            discount_amount = (subtotal * coupon.value) / 100

        final_total = max(0, subtotal - discount_amount)
        coupon_code = coupon.code
        coupon.usage_count += 1
        db.add(coupon)

    # Create the order
    new_order = models.Order(
        user_id=user_id,
        total=final_total,
        address=address_data,
        status=models.OrderStatus.PENDING,
        payment_status=models.PaymentStatus.PENDING,
        coupon_code=coupon_code,
        discount_amount=discount_amount
    )
    db.add(new_order)
    db.flush() # Flush to get the new_order.id

    # Create order items
    for item in cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.unit_price
        )
        db.add(order_item)

    # Clear the cart items
    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(new_order)
    return new_order


# --- Admin User CRUD ---
from src.admin_panel import schemas, security

def get_admin_user_by_name(db: Session, name: str) -> models.AdminUser | None:
    """
    Retrieves an admin user by their name.
    """
    return db.query(models.AdminUser).filter(models.AdminUser.name == name).first()

def create_admin_user(db: Session, user: schemas.AdminUserCreate) -> models.AdminUser:
    """
    Creates a new admin user with a hashed password.
    """
    hashed_password = security.get_password_hash(user.password)
    db_user = models.AdminUser(
        name=user.name,
        hashed_password=hashed_password,
        role=user.role,
        telegram_id=user.telegram_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Product CRUD for Admin Panel ---

def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_in: schemas.ProductUpdate) -> models.Product | None:
    db_product = get_product_by_id(db, product_id)
    if db_product:
        update_data = product_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> models.Product | None:
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product


# --- Category CRUD for Admin Panel ---

def get_category(db: Session, category_id: int) -> models.Category | None:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_all_categories(db: Session, skip: int = 0, limit: int = 100) -> list[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# --- Order CRUD for Admin Panel ---

def get_order(db: Session, order_id: int) -> models.Order | None:
    return db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id).first()

def get_all_orders(db: Session, skip: int = 0, limit: int = 100, status: str = None) -> list[models.Order]:
    query = db.query(models.Order).options(joinedload(models.Order.items))
    if status:
        query = query.filter(models.Order.status == status)
    return query.offset(skip).limit(limit).order_by(models.Order.created_at.desc()).all()

def update_order(db: Session, order_id: int, order_in: schemas.OrderUpdate) -> models.Order | None:
    db_order = get_order(db, order_id)
    if db_order:
        update_data = order_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value: # Ensure we don't update with None or empty strings
                setattr(db_order, key, value)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
    return db_order


# --- Coupon CRUD ---

def create_coupon(db: Session, coupon: schemas.CouponCreate) -> models.Coupon:
    db_coupon = models.Coupon(**coupon.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def get_coupon_by_code(db: Session, code: str) -> models.Coupon | None:
    return db.query(models.Coupon).filter(models.Coupon.code == code).first()

from datetime import timezone

def validate_coupon(db: Session, code: str) -> models.Coupon | None:
    """
    Checks if a coupon is valid for use.
    Returns the coupon object if valid, otherwise None.
    """
    coupon = get_coupon_by_code(db, code)
    if not coupon:
        return None
    if not coupon.is_active:
        return None
    if coupon.expires_at and coupon.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return None
    if coupon.usage_count >= coupon.usage_limit:
        return None
    return coupon


# --- Order History ---
from sqlalchemy import func
from datetime import datetime

def get_user_orders(db: Session, user_id: int) -> list[models.Order]:
    """
    Retrieves all orders for a specific user.
    """
    return db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()


# --- Reports CRUD ---
def get_sales_report(db: Session, start_date: datetime, end_date: datetime) -> dict:
    """
    Generates a sales report for a given date range.
    """
    # We only want to sum up orders that are not canceled.
    valid_statuses = [models.OrderStatus.CONFIRMED, models.OrderStatus.SHIPPING, models.OrderStatus.DELIVERED]

    query = (
        db.query(
            func.count(models.Order.id).label("total_orders"),
            func.sum(models.Order.total).label("total_revenue")
        )
        .filter(models.Order.created_at.between(start_date, end_date))
        .filter(models.Order.status.in_(valid_statuses))
    )

    result = query.one()

    return {
        "total_orders": result.total_orders or 0,
        "total_revenue": result.total_revenue or 0.0
    }
