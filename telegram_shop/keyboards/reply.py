# -*- coding: utf-8 -*-

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    """
    Creates the main menu reply keyboard.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🗂 دسته‌بندی‌ها"),
                KeyboardButton(text="🔍 جستجو محصول")
            ],
            [
                KeyboardButton(text="🛒 سبد خرید"),
                KeyboardButton(text="📦 سفارش‌های من")
            ],
            [
                KeyboardButton(text="📞 تماس با پشتیبانی")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Keep the keyboard open
    )
    return keyboard


def admin_main_keyboard():
    """
    Creates the main menu for the admin panel.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📈 آمار کلی"),
                KeyboardButton(text="📦 مدیریت سفارش‌ها")
            ],
            [
                KeyboardButton(text="➕ افزودن محصول"),
                KeyboardButton(text="📋 لیست محصولات")
            ],
            [
                KeyboardButton(text="⚙️ تنظیمات"),
                KeyboardButton(text="⬅️ بازگشت به منوی کاربر")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard
