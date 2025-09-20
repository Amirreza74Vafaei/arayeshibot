from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from src.db import crud, session as db_session
from src.bot.states import OrderPlacement
from src.core.config import settings

order_router = Router()

@order_router.callback_query(F.data == "checkout")
async def start_checkout(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Starts the order checkout process by asking for the user's address.
    """
    db: Session = next(db_session.get_db())
    user = crud.get_or_create_user(db, callback_query.from_user)
    cart_items = crud.get_cart_items(db, user_id=user.id)
    db.close()

    if not cart_items:
        await callback_query.answer("سبد خرید شما خالی است!", show_alert=True)
        return

    await callback_query.message.answer("لطفاً آدرس کامل خود را برای تحویل سفارش وارد کنید:")
    await state.set_state(OrderPlacement.waiting_for_address)
    await callback_query.answer()


@order_router.message(OrderPlacement.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    """
    Processes the user's address and asks for their phone number.
    """
    address = message.text
    await state.update_data(address=address)

    await message.answer("عالی! حالا لطفاً شماره تماس خود را وارد کنید:")
    await state.set_state(OrderPlacement.waiting_for_phone)


async def _show_confirmation(message: types.Message, state: FSMContext):
    """Helper function to show the confirmation message."""
    user_data = await state.get_data()
    address = user_data.get("address")
    phone = user_data.get("phone")
    coupon_code = user_data.get("coupon_code")

    db: Session = next(db_session.get_db())
    user = crud.get_or_create_user(db, message.from_user)
    cart_items = crud.get_cart_items(db, user_id=user.id)
    subtotal = sum(item.quantity * item.unit_price for item in cart_items)

    discount_amount = 0
    if coupon_code:
        coupon = crud.validate_coupon(db, coupon_code)
        if coupon:
            if coupon.discount_type == "fixed":
                discount_amount = min(coupon.value, subtotal)
            elif coupon.discount_type == "percent":
                discount_amount = (subtotal * coupon.value) / 100

    final_total = max(0, subtotal - discount_amount)
    db.close()

    confirmation_text = (
        " لطفاً اطلاعات سفارش خود را تأیید کنید:\n\n"
        f"<b>آدرس:</b> {address}\n"
        f"<b>تلفن:</b> {phone}\n\n"
        f"جمع محصولات: {subtotal:,.0f} تومان\n"
    )
    if discount_amount > 0:
        confirmation_text += f"تخفیف: <del>{discount_amount:,.0f} تومان</del>\n"

    confirmation_text += (
        f"<b>مبلغ کل: {final_total:,.0f} تومان</b>\n"
        "<b>روش پرداخت:</b> پرداخت درب منزل\n\n"
        "آیا همه چیز صحیح است؟"
    )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ بله، ثبت نهایی", callback_data="confirm_order")],
        [types.InlineKeyboardButton(text="❌ لغو و شروع مجدد", callback_data="cancel_order")]
    ])
    await message.answer(confirmation_text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(OrderPlacement.waiting_for_confirmation)

@order_router.message(OrderPlacement.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """
    Processes the user's phone number and asks for a coupon.
    """
    phone = message.text
    # Basic validation could be added here
    await state.update_data(phone=phone)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="رد شدن")]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("عالی! اگر کد تخفیف دارید، آن را وارد کنید. در غیر این صورت، «رد شدن» را بزنید.", reply_markup=keyboard)
    await state.set_state(OrderPlacement.waiting_for_coupon)


@order_router.message(OrderPlacement.waiting_for_coupon)
async def process_coupon(message: types.Message, state: FSMContext):
    """
    Processes the coupon code or skips the step.
    """
    # Remove the custom keyboard
    await message.answer("در حال بررسی...", reply_markup=types.ReplyKeyboardRemove())

    if message.text != "رد شدن":
        db: Session = next(db_session.get_db())
        coupon = crud.validate_coupon(db, code=message.text)
        db.close()
        if coupon:
            await state.update_data(coupon_code=coupon.code)
            await message.answer(f"✅ کد تخفیف «{coupon.code}» با موفقیت اعمال شد.")
        else:
            await message.answer("کد تخفیف نامعتبر است یا منقضی شده.")

    await _show_confirmation(message, state)


@order_router.callback_query(F.data == "confirm_order", OrderPlacement.waiting_for_confirmation)
async def process_final_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Processes the final confirmation, creates the order, and notifies the user and admin.
    """
    user_data = await state.get_data()
    db: Session = next(db_session.get_db())

    try:
        user = crud.get_or_create_user(db, callback_query.from_user)
        address_data = {"address": user_data.get("address"), "phone": user_data.get("phone")}

        coupon = None
        if user_data.get("coupon_code"):
            coupon = crud.validate_coupon(db, code=user_data.get("coupon_code"))

        new_order = crud.create_order_from_cart(db, user_id=user.id, address_data=address_data, coupon=coupon)

        # Success message to user
        await callback_query.message.edit_text(
            f"✅ سفارش شما با شماره #{new_order.id} با موفقیت ثبت شد.\n"
            "پرداخت درب منزل انجام خواهد شد. وضعیت سفارش را می‌توانید در بخش /orders ببینید."
        )

        # Notification to admin
        admin_message = (
            f"📢 سفارش جدید ثبت شد!\n"
            f"شماره سفارش: #{new_order.id}\n"
            f"مشتری: {user.first_name} (ID: {user.telegram_id})\n"
            f"مبلغ کل: {new_order.total:,.0f} تومان"
        )
        await callback_query.bot.send_message(settings.ADMIN_TELEGRAM_ID, admin_message)

    except ValueError as e:
        await callback_query.message.edit_text(f"خطایی رخ داد: {e}")
    except Exception as e:
        await callback_query.message.edit_text("یک خطای پیش‌بینی نشده رخ داد. لطفاً با پشتیبانی تماس بگیرید.")
        # Log the error
        logging.error(f"Could not create order: {e}")
    finally:
        await state.clear()
        db.close()
        await callback_query.answer()


@order_router.callback_query(F.data == "cancel_order")
async def cancel_order_process(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("فرآیند سفارش لغو شد. می‌توانید از نو شروع کنید.")
    await callback_query.answer()

@order_router.message(F.text == "📦 سفارش‌ها")
async def show_order_history(message: types.Message):
    """
    Displays the user's order history.
    """
    db: Session = next(db_session.get_db())
    user = crud.get_or_create_user(db, message.from_user)
    orders = crud.get_user_orders(db, user_id=user.id)
    db.close()

    if not orders:
        await message.answer("شما تاکنون هیچ سفارشی ثبت نکرده‌اید.")
        return

    history_text = "<b>📜 تاریخچه سفارشات شما:</b>\n\n"
    for order in orders:
        history_text += (
            f"<b>شماره سفارش:</b> #{order.id}\n"
            f"<b>تاریخ:</b> {order.created_at.strftime('%Y-%m-%d')}\n"
            f"<b>مبلغ کل:</b> {order.total:,.0f} تومان\n"
            f"<b>وضعیت:</b> {order.status.value}\n"
            f"--------------------\n"
        )

    await message.answer(history_text, parse_mode="HTML")
