# -*- coding: utf-8 -*-

import re
import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud
from keyboards import inline as inline_kb
from messages import *
from utils.states import Checkout
from handlers.user.cart import view_cart # To return to cart view

router = Router()

PHONE_REGEX = r"^(09\d{9})$" # Simple regex for Iranian phone numbers

# --- 1. Start Checkout Flow ---
@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    with get_db() as db:
        cart_items = crud.get_cart_items(db, callback.from_user.id)
        if not cart_items:
            await callback.answer("سبد خرید شما خالی است!", show_alert=True)
            return

    await state.set_state(Checkout.waiting_for_name)
    await callback.message.answer(CHECKOUT_PROMPT_NAME)
    await callback.answer()

# --- 2. Receive Name ---
@router.message(Checkout.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Checkout.waiting_for_phone)
    await message.answer(CHECKOUT_PROMPT_PHONE)

# --- 3. Receive Phone Number ---
@router.message(Checkout.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if not re.match(PHONE_REGEX, message.text):
        await message.answer(CHECKOUT_INVALID_PHONE)
        return

    await state.update_data(phone=message.text)
    await state.set_state(Checkout.waiting_for_address)
    await message.answer(CHECKOUT_PROMPT_ADDRESS)

# --- 4. Receive Address & Show Confirmation ---
@router.message(Checkout.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)

    user_data = await state.get_data()
    user_id = message.from_user.id

    with get_db() as db:
        cart_items = crud.get_cart_items(db, user_id)
        # Create order summary text
        summary_text = ""
        total_price = 0
        for i, item in enumerate(cart_items, 1):
            item_total = item.product.price * item.quantity
            total_price += item_total
            summary_text += CART_ITEM_LINE.format(
                index=i, name=item.product.name, quantity=item.quantity,
                price=f"{item.product.price:,.0f}", total_price=f"{item_total:,.0f}"
            )

        # Get shipping cost from settings, default to 0 if not set
        shipping_cost_str = crud.get_setting(db, "shipping_cost")
        shipping_cost = float(shipping_cost_str) if shipping_cost_str else 0.0
        final_total = total_price + shipping_cost

        await state.update_data(shipping_cost=shipping_cost)

        confirmation_text = CHECKOUT_CONFIRMATION.format(
            name=user_data['name'],
            phone=user_data['phone'],
            address=user_data['address'],
            summary=summary_text,
            shipping_cost=f"{shipping_cost:,.0f}",
            final_total=f"{final_total:,.0f}"
        )

    await state.set_state(Checkout.confirming_order)
    await message.answer(confirmation_text, reply_markup=inline_kb.checkout_confirmation_keyboard())

# --- 5. Handle Final Confirmation or Cancellation ---
@router.callback_query(Checkout.confirming_order)
async def process_confirmation(callback: types.CallbackQuery, state: FSMContext, bot: types.Bot):
    if callback.data == "checkout_confirm":
        user_data = await state.get_data()
        user_id = callback.from_user.id

        with get_db() as db:
            # Create the order in the database
            order = crud.create_order(db, user_id, user_data)
            if not order:
                await callback.answer("خطا در ثبت سفارش. سبد خرید شما خالی است.", show_alert=True)
                await state.clear()
                return

            # Clear the user's cart
            crud.clear_cart(db, user_id)

            # Notify the user
            await callback.message.edit_text(ORDER_SUCCESS_USER.format(order_uid=order.order_uid))

            # Notify admin
            admin_channel_id = os.getenv("ADMIN_CHANNEL_ID")
            if admin_channel_id:
                items_summary = ""
                for item in order.items:
                    items_summary += f"- {item.product.name} (تعداد: {item.quantity})\n"

                final_total = order.total_amount + order.shipping_cost
                admin_message = NEW_ORDER_ADMIN_NOTIFICATION.format(
                    order_uid=order.order_uid,
                    user_link=f"<a href='tg://user?id={user_id}'>{callback.from_user.full_name}</a>",
                    user_id=user_id,
                    recipient_name=order.recipient_name,
                    recipient_phone=order.recipient_phone,
                    shipping_address=order.shipping_address,
                    items_summary=items_summary,
                    total_amount=f"{order.total_amount:,.0f}",
                    shipping_cost=f"{order.shipping_cost:,.0f}",
                    final_total=f"{final_total:,.0f}"
                )
                try:
                    await bot.send_message(admin_channel_id, admin_message, parse_mode="HTML")
                except Exception as e:
                    # Log this error, e.g., bot not in channel, wrong ID etc.
                    print(f"Failed to send admin notification: {e}")

        await callback.answer("✅ سفارش شما با موفقیت ثبت شد.")
        await state.clear()

    elif callback.data == "checkout_cancel":
        await state.clear()
        await callback.message.delete() # Remove the confirmation message
        # Show the cart again
        await view_cart(callback)
        await callback.answer("ثبت سفارش لغو شد.")
