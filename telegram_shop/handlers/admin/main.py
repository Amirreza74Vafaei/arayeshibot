# -*- coding: utf-8 -*-

from aiogram import Router, types, F
from aiogram.filters import Command

from filters.is_admin import IsAdmin
from keyboards.reply import admin_main_keyboard, main_menu_keyboard

router = Router()

# This router should only be activated for admins
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

@router.message(Command("admin"))
async def admin_panel_start(message: types.Message):
    """
    Entry point for the admin panel.
    Shows the admin main menu.
    """
    await message.answer(
        "👋 خوش آمدید به پنل مدیریت!",
        reply_markup=admin_main_keyboard()
    )

@router.message(F.text == "⬅️ بازگشت به منوی کاربر")
async def return_to_user_menu(message: types.Message):
    """
    Allows an admin to switch back to the regular user view.
    """
    await message.answer(
        "شما به منوی کاربری بازگشتید.",
        reply_markup=main_menu_keyboard()
    )

@router.message(F.text == "📈 آمار کلی")
async def show_stats(message: types.Message):
    """
    Placeholder for showing store statistics.
    """
    # In a real application, you would query the database for stats.
    # For example: number of users, number of orders, total revenue, etc.
    stats_text = (
        "<b>📊 آمار فروشگاه (نمونه)</b>\n\n"
        "- تعداد کاربران: <b>150</b>\n"
        "- تعداد سفارش‌های جدید: <b>5</b>\n"
        "- مجموع فروش امروز: <b>1,250,000 تومان</b>"
    )
    await message.answer(stats_text)
