from sqlalchemy.orm import Session
from . import models

# --- Category Functions ---
def get_categories(db: Session):
    """Returns all categories from the database."""
    return db.query(models.Category).all()

def get_category(db: Session, category_id: int):
    """Returns a single category by its ID."""
    return db.query(models.Category).filter(models.Category.id == category_id).first()

# --- Product Functions ---
def get_products_by_category(db: Session, category_id: int):
    """Returns all products belonging to a specific category."""
    return db.query(models.Product).filter(models.Product.category_id == category_id).all()

def get_product(db: Session, product_id: int):
    """Returns a single product by its ID."""
    return db.query(models.Product).filter(models.Product.id == product_id).first()

# --- User Functions ---
def get_or_create_user(db: Session, user_data: dict):
    """
    Retrieves a user by their Telegram ID, creating them if they don't exist.
    """
    user = db.query(models.User).filter(models.User.id == user_data['id']).first()
    if not user:
        user = models.User(
            id=user_data['id'],
            username=user_data.get('username'),
            full_name=user_data['full_name'],
            language_code=user_data.get('language_code')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# --- Cart Functions ---
def get_cart_items(db: Session, user_id: int):
    """Returns all cart items for a specific user."""
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def add_item_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1):
    """Adds a product to the user's cart or increases its quantity if it already exists."""
    # Check if the item is already in the cart
    cart_item = db.query(models.CartItem).filter_by(user_id=user_id, product_id=product_id).first()
    product = get_product(db, product_id)

    if not product or product.quantity < 1:
        return None # Product does not exist or is out of stock

    if cart_item:
        # Item exists, increase quantity if stock allows
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.quantity:
            # Cannot add more than available stock
            return None
        cart_item.quantity = new_quantity
    else:
        # Item does not exist, create a new one
        if quantity > product.quantity:
            return None
        cart_item = models.CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_item_from_cart(db: Session, user_id: int, product_id: int):
    """Removes an item completely from the user's cart."""
    cart_item = db.query(models.CartItem).filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
        return True
    return False

def update_cart_item_quantity(db: Session, user_id: int, product_id: int, new_quantity: int):
    """Updates the quantity of a specific item in the cart."""
    cart_item = db.query(models.CartItem).filter_by(user_id=user_id, product_id=product_id).first()
    product = get_product(db, product_id)

    if not cart_item or not product:
        return None

    if new_quantity > 0 and new_quantity <= product.quantity:
        cart_item.quantity = new_quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item
    elif new_quantity <= 0:
        # If quantity is zero or less, remove the item
        db.delete(cart_item)
        db.commit()
        return None # Indicate removal
    else:
        # Requested quantity exceeds stock
        return "out_of_stock"


def clear_cart(db: Session, user_id: int):
    """Removes all items from a user's cart."""
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()


# --- Order Functions ---
def create_order(db: Session, user_id: int, details: dict) -> models.Order:
    """
    Creates a new order and associated order items from the user's cart.
    """
    cart_items = get_cart_items(db, user_id)
    if not cart_items:
        return None

    # Calculate total amount from cart items
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    # A simple UID generation scheme. In a real-world scenario, this should be more robust.
    from datetime import datetime
    order_uid = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"

    # Create the main order record
    new_order = models.Order(
        order_uid=order_uid,
        user_id=user_id,
        status="NEW",
        total_amount=total_amount,
        shipping_cost=details['shipping_cost'], # Assuming this is passed in details
        recipient_name=details['name'],
        recipient_phone=details['phone'],
        shipping_address=details['address']
    )
    db.add(new_order)
    db.flush() # Use flush to get the new_order.id before committing

    # Create order items and decrease product stock
    for item in cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_per_item=item.product.price
        )
        db.add(order_item)

        # Decrease product stock
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.quantity -= item.quantity

    db.commit()
    db.refresh(new_order)
    return new_order

def get_orders_by_user(db: Session, user_id: int):
    """Returns all orders for a specific user, most recent first."""
    return db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()

def get_order_by_uid(db: Session, order_uid: str):
    """Returns a single order by its public-facing UID."""
    return db.query(models.Order).filter(models.Order.order_uid == order_uid).first()


# --- Admin: Product Management ---
def create_product(db: Session, product_data: dict) -> models.Product:
    """Creates a new product."""
    new_product = models.Product(**product_data)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    """Returns all orders, with pagination."""
    return db.query(models.Order).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def get_orders_by_status(db: Session, status: str):
    """Returns all orders with a specific status."""
    return db.query(models.Order).filter(models.Order.status == status).order_by(models.Order.created_at.desc()).all()

def update_order_status(db: Session, order_uid: str, new_status: str) -> models.Order:
    """Updates the status of a specific order."""
    order = get_order_by_uid(db, order_uid)
    if order:
        order.status = new_status
        db.commit()
        db.refresh(order)
    return order


# --- Settings Functions ---
def get_setting(db: Session, key: str) -> str:
    """Gets a setting value by its key."""
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    return setting.value if setting else None

def set_setting(db: Session, key: str, value: str):
    """Creates or updates a setting."""
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    return setting
