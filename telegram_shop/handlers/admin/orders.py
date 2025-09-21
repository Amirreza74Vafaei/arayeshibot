# -*- coding: utf-8 -*-

from aiogram import Router, types, F, Bot
from sqlalchemy.orm import Session

from filters.is_admin import IsAdmin
from db.database import get_db
from db import crud
from keyboards import inline as inline_kb
from handlers.user.orders import STATUS_TRANSLATIONS # Reuse translations

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

async def get_order_details_text(order: crud.models.Order) -> str:
    """Helper to format order details into a string for messages."""
    items_summary = ""
    for item in order.items:
        items_summary += f"- {item.product.name} (تعداد: {item.quantity})\n"

    final_total = order.total_amount + order.shipping_cost
    status_fa = STATUS_TRANSLATIONS.get(order.status, order.status)

    return (
        f"<b>جزئیات سفارش {order.order_uid}</b>\n\n"
        f"<b>وضعیت:</b> {status_fa}\n"
        f"<b>کاربر:</b> <a href='tg://user?id={order.user_id}'>{order.user.full_name}</a> (ID: {order.user_id})\n"
        f"<b>گیرنده:</b> {order.recipient_name}\n"
        f"<b>تلفن:</b> {order.recipient_phone}\n"
        f"<b>آدرس:</b> {order.shipping_address}\n\n"
        f"<b>آیتم‌ها:</b>\n{items_summary}\n"
        f"<b>جمع کل:</b> {final_total:,.0f} تومان"
    )

@router.message(F.text == "📦 مدیریت سفارش‌ها")
async def handle_manage_orders(message: types.Message):
    """Shows the order filtering keyboard."""
    await message.answer(
        "یک دسته از سفارش‌ها را برای مشاهده انتخاب کنید:",
        reply_markup=inline_kb.admin_order_filters_keyboard()
    )

@router.callback_query(F.data == "admin_back_to_order_filters")
async def back_to_order_filters(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "یک دسته از سفارش‌ها را برای مشاهده انتخاب کنید:",
        reply_markup=inline_kb.admin_order_filters_keyboard()
    )

@router.callback_query(F.data.startswith("admin_filter_order_"))
async def list_filtered_orders(callback: types.CallbackQuery):
    status = callback.data.split("admin_filter_order_")[1]

    with get_db() as db:
        if status == "ALL":
            orders = crud.get_all_orders(db, limit=20) # Limit to avoid huge messages
        else:
            orders = crud.get_orders_by_status(db, status)

    if not orders:
        await callback.answer("هیچ سفارشی با این وضعیت یافت نشد.", show_alert=True)
        return

    text = f"لیست سفارش‌ها با وضعیت: <b>{STATUS_TRANSLATIONS.get(status, 'همه')}</b>\n\n"
    builder = types.InlineKeyboardBuilder()
    for order in orders:
        order_date = order.created_at.strftime('%y-%m-%d')
        builder.button(
            text=f"{order.order_uid} - {order.recipient_name} - {order_date}",
            callback_data=f"admin_view_order_{order.order_uid}"
        )
    builder.adjust(1)
    builder.row(types.InlineKeyboardButton(text="⬅️ بازگشت", callback_data="admin_back_to_order_filters"))

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_view_order_"))
async def admin_view_order(callback: types.CallbackQuery):
    order_uid = callback.data.split("admin_view_order_")[1]
    with get_db() as db:
        order = crud.get_order_by_uid(db, order_uid)
        if not order:
            await callback.answer("سفارش یافت نشد", show_alert=True)
            return

        text = await get_order_details_text(order)
        keyboard = inline_kb.admin_order_actions_keyboard(order.order_uid)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# --- Order Action Handlers ---
async def handle_status_change(callback: types.CallbackQuery, bot: Bot, order_uid: str, new_status: str, user_message: str):
    with get_db() as db:
        order = crud.update_order_status(db, order_uid, new_status)
        if order:
            # Notify user
            try:
                await bot.send_message(order.user_id, user_message)
            except Exception as e:
                print(f"Failed to send status update to user {order.user_id}: {e}")

            # Update admin view
            text = await get_order_details_text(order)
            keyboard = inline_kb.admin_order_actions_keyboard(order.order_uid)
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer(f"✅ وضعیت سفارش به '{STATUS_TRANSLATIONS.get(new_status)}' تغییر کرد.")
        else:
            await callback.answer("❌ سفارش یافت نشد.", show_alert=True)

@router.callback_query(F.data.startswith("admin_accept_order_"))
async def accept_order(callback: types.CallbackQuery, bot: Bot):
    order_uid = callback.data.split("admin_accept_order_")[1]
    user_message = f"✅ سفارش شما با شناسه {order_uid} تأیید شد و در حال آماده‌سازی است."
    await handle_status_change(callback, bot, order_uid, "ACCEPTED", user_message)

@router.callback_query(F.data.startswith("admin_ship_order_"))
async def ship_order(callback: types.CallbackQuery, bot: Bot):
    order_uid = callback.data.split("admin_ship_order_")[1]
    user_message = f"🚚 سفارش شما با شناسه {order_uid} ارسال شد و به‌زودی به دستتان خواهد رسید."
    await handle_status_change(callback, bot, order_uid, "SHIPPED", user_message)

@router.callback_query(F.data.startswith("admin_cancel_order_"))
async def cancel_order(callback: types.CallbackQuery, bot: Bot):
    order_uid = callback.data.split("admin_cancel_order_")[1]
    user_message = f"❌ متاسفانه سفارش شما با شناسه {order_uid} لغو شد. برای اطلاعات بیشتر با پشتیبانی تماس بگیرید."
    await handle_status_change(callback, bot, order_uid, "CANCELED", user_message)
