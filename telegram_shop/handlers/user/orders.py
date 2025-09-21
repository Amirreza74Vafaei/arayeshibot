# -*- coding: utf-8 -*-

from aiogram import Router, types, F
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud
from keyboards import inline as inline_kb

router = Router()

# A mapping from status codes to user-friendly Farsi names
STATUS_TRANSLATIONS = {
    "NEW": "جدید",
    "ACCEPTED": "تأیید شده",
    "SHIPPED": "ارسال شده",
    "DELIVERED": "تحویل شده",
    "CANCELED": "لغو شده",
}


async def list_user_orders(message_or_callback: types.Message | types.CallbackQuery):
    """Helper function to show the list of user's orders."""
    user_id = message_or_callback.from_user.id
    with get_db() as db:
        orders = crud.get_orders_by_user(db, user_id)
        if not orders:
            text = "شما تاکنون هیچ سفارشی ثبت نکرده‌اید."
            keyboard = None
        else:
            text = "سفارش‌های شما:"
            keyboard = inline_kb.order_history_keyboard(orders)

    if isinstance(message_or_callback, types.CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=keyboard)
    else:
        await message_or_callback.answer(text, reply_markup=keyboard)


@router.message(F.text == "📦 سفارش‌های من")
async def handle_my_orders_button(message: types.Message):
    """Handles the 'My Orders' button click."""
    await list_user_orders(message)


@router.callback_query(F.data.startswith("view_order_"))
async def view_order_details(callback: types.CallbackQuery):
    """Displays the details of a specific order."""
    order_uid = callback.data.split("view_order_")[1]

    with get_db() as db:
        order = crud.get_order_by_uid(db, order_uid)
        if not order or order.user_id != callback.from_user.id:
            await callback.answer("سفارش یافت نشد.", show_alert=True)
            return

        items_summary = ""
        for item in order.items:
            items_summary += f"- {item.product.name} (تعداد: {item.quantity} عدد × {item.price_per_item:,.0f} تومان)\n"

        final_total = order.total_amount + order.shipping_cost
        status_fa = STATUS_TRANSLATIONS.get(order.status, order.status)

        text = (
            f"<b>جزئیات سفارش {order.order_uid}</b>\n\n"
            f"<b>وضعیت:</b> {status_fa}\n"
            f"<b>تاریخ ثبت:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"<b>گیرنده:</b> {order.recipient_name}\n"
            f"<b>تلفن:</b> {order.recipient_phone}\n"
            f"<b>آدرس:</b> {order.shipping_address}\n\n"
            f"<b>آیتم‌های سفارش:</b>\n{items_summary}\n"
            f"<b>جمع مبلغ محصولات:</b> {order.total_amount:,.0f} تومان\n"
            f"<b>هزینه ارسال:</b> {order.shipping_cost:,.0f} تومان\n"
            f"<b>مبلغ نهایی:</b> {final_total:,.0f} تومان"
        )

        keyboard = inline_kb.order_detail_keyboard()
        await callback.message.edit_text(text, reply_markup=keyboard)

    await callback.answer()

@router.callback_query(F.data == "back_to_orders")
async def back_to_order_list(callback: types.CallbackQuery):
    """Handles the 'Back to Orders' button."""
    await list_user_orders(callback)
    await callback.answer()
