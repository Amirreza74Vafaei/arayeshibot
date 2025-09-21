# -*- coding: utf-8 -*-

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from db.models import Category, Product

# Using callback data factories can make handling callbacks cleaner,
# but for this project, simple strings are sufficient and easier to understand.
# Example callback_data formats:
# "select_category_{category_id}"
# "view_product_{product_id}"
# "add_to_cart_{product_id}"
# "back_to_categories"
# "back_to_products_{category_id}"


def categories_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with a list of categories.
    """
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=f"select_category_{category.id}"
        )
    builder.adjust(2)  # Arrange buttons in 2 columns
    return builder.as_markup()


def products_keyboard(products: List[Product], category_id: int) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with a list of products in a category.
    """
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} - {product.price} تومان",
            callback_data=f"view_product_{product.id}"
        )
    # Add a button to go back to the category list
    builder.button(text="⬅️ بازگشت به دسته‌بندی‌ها", callback_data="back_to_categories")
    builder.adjust(1)  # Arrange buttons in 1 column
    return builder.as_markup()


def product_details_keyboard(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for the product details view.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ افزودن به سبد خرید", callback_data=f"add_to_cart_{product_id}")
    builder.button(text="⬅️ بازگشت به لیست محصولات", callback_data=f"back_to_products_{category_id}")
    return builder.as_markup()


def cart_keyboard(cart_items: List) -> InlineKeyboardMarkup:
    """
    Creates the inline keyboard for the shopping cart view.
    """
    builder = InlineKeyboardBuilder()
    # For each item, add a row of buttons: -, quantity, +, remove
    for item in cart_items:
        product_id = item.product_id
        quantity = item.quantity

        builder.button(text="➖", callback_data=f"cart_decrease_{product_id}")
        builder.button(text=f"{quantity}", callback_data="cart_ignore") # Just a display
        builder.button(text="➕", callback_data=f"cart_increase_{product_id}")
        builder.button(text="❌ حذف", callback_data=f"cart_remove_{product_id}")

    # Set the layout for the item rows
    if cart_items:
        builder.adjust(*([4] * len(cart_items))) # 4 buttons per row for each item

    # Add a checkout button at the end
    builder.row(
        InlineKeyboardButton(text="✅ ثبت سفارش و پرداخت درب منزل", callback_data="checkout_start")
    )
    return builder.as_markup()


def checkout_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Creates the keyboard for the final checkout confirmation step.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ تأیید و ثبت نهایی", callback_data="checkout_confirm")
    builder.button(text="❌ لغو و بازگشت به سبد", callback_data="checkout_cancel")
    return builder.as_markup()


def order_history_keyboard(orders: List) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with a list of user's past orders.
    """
    builder = InlineKeyboardBuilder()
    for order in orders:
        # Format date to be more readable
        order_date = order.created_at.strftime('%Y-%m-%d')
        builder.button(
            text=f"سفارش {order.order_uid} - {order_date}",
            callback_data=f"view_order_{order.order_uid}"
        )
    builder.adjust(1)
    return builder.as_markup()


def order_detail_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for the detailed order view.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ بازگشت به لیست سفارش‌ها", callback_data="back_to_orders")
    # Optional: Add a "Reorder" button
    # builder.button(text="🔁 سفارش مجدد", callback_data=f"reorder_{order.order_uid}")
    return builder.as_markup()


def admin_categories_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for category selection in the admin panel.
    """
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=f"admin_select_category_{category.id}"
        )
    builder.adjust(2)
    # Add a cancel button
    builder.row(InlineKeyboardButton(text="❌ لغو عملیات", callback_data="admin_cancel_add_product"))
    return builder.as_markup()


def admin_order_filters_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with buttons to filter orders by status."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🆕 سفارش‌های جدید", callback_data="admin_filter_order_NEW")
    builder.button(text="✅ تأیید شده", callback_data="admin_filter_order_ACCEPTED")
    builder.button(text="🚚 ارسال شده", callback_data="admin_filter_order_SHIPPED")
    builder.button(text="✔️ تحویل شده", callback_data="admin_filter_order_DELIVERED")
    builder.button(text="❌ لغو شده", callback_data="admin_filter_order_CANCELED")
    builder.button(text=" همه سفارش‌ها", callback_data="admin_filter_order_ALL")
    builder.adjust(2)
    return builder.as_markup()


def admin_order_actions_keyboard(order_uid: str) -> InlineKeyboardMarkup:
    """Keyboard with actions for a specific order."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ تأیید سفارش", callback_data=f"admin_accept_order_{order_uid}")
    builder.button(text="🚚 ثبت ارسال", callback_data=f"admin_ship_order_{order_uid}")
    builder.button(text="❌ لغو سفارش", callback_data=f"admin_cancel_order_{order_uid}")
    builder.button(text="⬅️ بازگشت به لیست", callback_data="admin_back_to_order_filters")
    builder.adjust(1)
    return builder.as_markup()
