from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Returns the main menu keyboard.
    """
    products_button = KeyboardButton(text="🛍️ محصولات")
    orders_button = KeyboardButton(text="📦 سفارش‌ها")
    support_button = KeyboardButton(text="📞 تماس با پشتیبانی")
    about_us_button = KeyboardButton(text="ℹ️ درباره ما")

    cart_button = KeyboardButton(text="🛒 سبد خرید")

    # The keyboard layout
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [products_button],
            [cart_button, orders_button],
            [support_button, about_us_button]
        ],
        resize_keyboard=True,
        input_field_placeholder="از منوی زیر انتخاب کنید:"
    )
    return keyboard
