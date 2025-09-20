from aiogram import Router, types, F
from sqlalchemy.orm import Session

from src.db import crud, session as db_session

cart_router = Router()

@cart_router.callback_query(F.data.startswith("add_to_cart:"))
async def add_to_cart_handler(callback_query: types.CallbackQuery):
    """
    Handles adding an item to the shopping cart.
    """
    try:
        _, product_id_str = callback_query.data.split(":")
        product_id = int(product_id_str)
    except (ValueError, IndexError):
        await callback_query.answer("خطای اطلاعات دریافتی.", show_alert=True)
        return

    db: Session = next(db_session.get_db())

    # We need the user's database ID, not their telegram_id, for cart operations
    user = crud.get_or_create_user(db, callback_query.from_user)
    product = crud.get_product_by_id(db, product_id)

    if not product:
        await callback_query.answer("محصول یافت نشد!", show_alert=True)
        db.close()
        return

    try:
        crud.add_item_to_cart(db, user_id=user.id, product_id=product_id)
        await callback_query.answer(
            f"✅ «{product.title}» به سبد خرید اضافه شد.",
            show_alert=False # Shows a brief notification at the top of the screen
        )
    except ValueError as e:
        await callback_query.answer(f"خطا: {e}", show_alert=True)
    finally:
        db.close()

from src.bot.keyboards.inline_keyboards import get_cart_view_keyboard

@cart_router.message(F.text == "🛒 سبد خرید")
async def view_cart_handler(message: types.Message):
    """
    Displays the contents of the user's shopping cart.
    """
    db: Session = next(db_session.get_db())
    user = crud.get_or_create_user(db, message.from_user)
    cart_items = crud.get_cart_items(db, user_id=user.id)

    if not cart_items:
        await message.answer("سبد خرید شما خالی است.")
        db.close()
        return

    cart_text = "🛒 <b>سبد خرید شما:</b>\n\n"
    total_price = 0

    for item in cart_items:
        # The relationship should load the product details
        subtotal = item.quantity * item.unit_price
        total_price += subtotal
        cart_text += (
            f"▪️ <b>{item.product.title}</b>\n"
            f"   {item.quantity} عدد × {item.unit_price:,.0f} تومان = {subtotal:,.0f} تومان\n"
        )

    cart_text += f"\n<b>جمع کل: {total_price:,.0f} تومان</b>"

    keyboard = get_cart_view_keyboard(cart_items)
    await message.answer(cart_text, reply_markup=keyboard, parse_mode="HTML")
    db.close()
