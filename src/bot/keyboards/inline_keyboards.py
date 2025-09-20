from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from src.db.models import Category

from src.db.models import Product

def get_categories_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with buttons for each product category.
    """
    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.button(
            text=category.title,
            callback_data=f"category:{category.id}:1"  # category:cat_id:page
        )

    builder.adjust(2)
    return builder.as_markup()

def get_products_keyboard(
    products: List[Product],
    total_products: int,
    category_id: int,
    page: int,
    page_size: int
) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for a paginated list of products.
    """
    builder = InlineKeyboardBuilder()

    # Product buttons
    for product in products:
        builder.button(
            text=f"{product.title} - {product.price:,.0f} تومان",
            callback_data=f"product:{product.id}"
        )
    builder.adjust(1) # Each product on its own row

    # Pagination buttons
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(text="⬅️ قبلی", callback_data=f"category:{category_id}:{page-1}")
        )

    total_pages = (total_products + page_size - 1) // page_size
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(text="بعدی ➡️", callback_data=f"category:{category_id}:{page+1}")
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    # Add a back button
    builder.row(InlineKeyboardButton(text="🔙 بازگشت به دسته‌بندی‌ها", callback_data="back_to_categories"))

    return builder.as_markup()


def get_product_detail_keyboard(product: Product) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for the product detail view.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="➕ افزودن به سبد خرید",
        callback_data=f"add_to_cart:{product.id}"
    )
    builder.button(
        text="🔙 بازگشت به لیست محصولات",
        callback_data=f"category:{product.category_id}:1" # Go back to page 1 of the category
    )
    builder.adjust(1)

    return builder.as_markup()


def get_cart_view_keyboard(cart_items: List) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for viewing and managing the shopping cart.
    """
    builder = InlineKeyboardBuilder()

    # Create rows for each item with quantity controls
    for item in cart_items:
        builder.button(text=f"❌", callback_data=f"cart_rem:{item.product_id}")
        builder.button(text=f"{item.quantity}", callback_data="noop") # No-op button
        builder.button(text=f"➕", callback_data=f"cart_add:{item.product_id}")

    # Adjust to have 3 buttons per row (remove, quantity, add)
    if cart_items:
        builder.adjust(3)

    # Add main action buttons
    builder.row(
        InlineKeyboardButton(text="💳 تسویه حساب", callback_data="checkout"),
        InlineKeyboardButton(text="🗑️ خالی کردن سبد", callback_data="cart_clear"),
    )
    builder.row(
        InlineKeyboardButton(text="🛍 ادامه خرید", callback_data="back_to_categories")
    )

    return builder.as_markup()
