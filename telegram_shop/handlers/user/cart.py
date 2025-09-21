# -*- coding: utf-8 -*-

from aiogram import Router, types, F
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud
from keyboards import inline as inline_kb
from messages import CART_EMPTY, CART_HEADER, CART_ITEM_LINE, CART_FOOTER

router = Router()

async def view_cart(message_or_callback: types.Message | types.CallbackQuery):
    """
    A helper function to display the user's cart.
    Can be called from a message handler or a callback query handler.
    """
    user_id = message_or_callback.from_user.id

    with get_db() as db:
        cart_items = crud.get_cart_items(db, user_id)

        if not cart_items:
            text = CART_EMPTY
            keyboard = None
        else:
            text = CART_HEADER
            total_price = 0
            for i, item in enumerate(cart_items, 1):
                item_total = item.product.price * item.quantity
                total_price += item_total
                text += CART_ITEM_LINE.format(
                    index=i,
                    name=item.product.name,
                    quantity=item.quantity,
                    price=f"{item.product.price:,.0f}",
                    total_price=f"{item_total:,.0f}"
                )
            text += CART_FOOTER.format(total=f"{total_price:,.0f}")
            keyboard = inline_kb.cart_keyboard(cart_items)

    # If it's a callback, edit the message. If it's a message, send a new one.
    if isinstance(message_or_callback, types.CallbackQuery):
        # Avoid editing if the text is the same, which can cause an error
        if message_or_callback.message.text != text:
             await message_or_callback.message.edit_text(text, reply_markup=keyboard)
        await message_or_callback.answer()
    else: # It's a Message
        await message_or_callback.answer(text, reply_markup=keyboard)


@router.message(F.text == "🛒 سبد خرید")
async def handle_cart_button(message: types.Message):
    """Handles the 'Shopping Cart' button click."""
    await view_cart(message)


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart_callback(callback: types.CallbackQuery):
    """Handles 'Add to Cart' button clicks from product pages."""
    product_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id

    with get_db() as db:
        cart_item = crud.add_item_to_cart(db, user_id=user_id, product_id=product_id, quantity=1)
        if cart_item:
            await callback.answer(f"✅ محصول به سبد خرید اضافه شد.", show_alert=False)
        else:
            await callback.answer("❌ موجودی محصول کافی نیست.", show_alert=True)


@router.callback_query(F.data.startswith("cart_"))
async def handle_cart_actions(callback: types.CallbackQuery):
    """Handles all actions within the cart view (increase, decrease, remove)."""
    action, product_id_str = callback.data.split("_")[1], callback.data.split("_")[2]
    product_id = int(product_id_str)
    user_id = callback.from_user.id

    with get_db() as db:
        cart_item = db.query(crud.models.CartItem).filter_by(user_id=user_id, product_id=product_id).first()
        if not cart_item:
            await callback.answer("این آیتم در سبد شما نیست.", show_alert=True)
            return

        if action == "increase":
            crud.update_cart_item_quantity(db, user_id, product_id, cart_item.quantity + 1)
        elif action == "decrease":
            new_quantity = cart_item.quantity - 1
            if new_quantity > 0:
                crud.update_cart_item_quantity(db, user_id, product_id, new_quantity)
            else:
                crud.remove_item_from_cart(db, user_id, product_id)
        elif action == "remove":
            crud.remove_item_from_cart(db, user_id, product_id)

    # Refresh the cart view
    await view_cart(callback)
