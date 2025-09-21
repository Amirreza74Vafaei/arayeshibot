# -*- coding: utf-8 -*-

import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from filters.is_admin import IsAdmin
from utils.states import AdminProduct
from db.database import get_db
from db import crud
from keyboards import inline as inline_kb

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

# --- Add Product FSM ---

# 1. Start the "Add Product" flow
@router.message(F.text == "➕ افزودن محصول")
async def start_add_product(message: types.Message, state: FSMContext):
    await state.set_state(AdminProduct.waiting_for_name)
    await message.answer("لطفاً نام محصول جدید را وارد کنید:")

# Handler for cancelling the FSM
@router.callback_query(F.data == "admin_cancel_add_product")
async def cancel_add_product(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("عملیات افزودن محصول لغو شد.")
    await callback.answer()

# 2. Get product name
@router.message(AdminProduct.waiting_for_name)
async def process_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminProduct.waiting_for_description)
    await message.answer("توضیحات محصول را وارد کنید:")

# 3. Get product description
@router.message(AdminProduct.waiting_for_description)
async def process_product_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminProduct.waiting_for_price)
    await message.answer("قیمت محصول را به تومان وارد کنید (فقط عدد):")

# 4. Get product price
@router.message(AdminProduct.waiting_for_price)
async def process_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("قیمت نامعتبر است. لطفاً فقط عدد وارد کنید.")
        return
    await state.update_data(price=price)
    await state.set_state(AdminProduct.waiting_for_quantity)
    await message.answer("موجودی اولیه محصول را وارد کنید:")

# 5. Get product quantity
@router.message(AdminProduct.waiting_for_quantity)
async def process_product_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
    except ValueError:
        await message.answer("موجودی نامعتبر است. لطفاً فقط عدد صحیح وارد کنید.")
        return
    await state.update_data(quantity=quantity)
    await state.set_state(AdminProduct.waiting_for_category)

    with get_db() as db:
        categories = crud.get_categories(db)
        keyboard = inline_kb.admin_categories_keyboard(categories)
        await message.answer("دسته‌بندی محصول را انتخاب کنید:", reply_markup=keyboard)

# 6. Get product category
@router.callback_query(AdminProduct.waiting_for_category, F.data.startswith("admin_select_category_"))
async def process_product_category(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminProduct.waiting_for_image)
    await callback.message.edit_text("تصویر اصلی محصول را ارسال کنید:")
    await callback.answer()

# 7. Get product image and finalize
@router.message(AdminProduct.waiting_for_image, F.photo)
async def process_product_image(message: types.Message, state: FSMContext, bot: types.Bot):
    photo = message.photo[-1] # Get the highest resolution photo

    # Create a unique filename
    file_name = f"{photo.file_unique_id}.jpg"
    file_path = os.path.join("telegram_shop/assets/images", file_name)

    # Download the file
    await bot.download(file=photo.file_id, destination=file_path)

    await state.update_data(image_path=file_name)
    product_data = await state.get_data()

    # Create product in DB
    with get_db() as db:
        crud.create_product(db, product_data)

    await message.answer(f"✅ محصول '{product_data['name']}' با موفقیت اضافه شد.")
    await state.clear()


# --- List Products ---
@router.message(F.text == "📋 لیست محصولات")
async def list_products(message: types.Message):
    # This is a simplified version. A real implementation would use pagination.
    with get_db() as db:
        products = db.query(crud.models.Product).all()
        if not products:
            await message.answer("هیچ محصولی یافت نشد.")
            return

        response_text = "<b>لیست تمام محصولات:</b>\n\n"
        for p in products:
            response_text += f"- <b>نام:</b> {p.name}\n"
            response_text += f"  <b>ID:</b> <code>{p.id}</code>\n"
            response_text += f"  <b>قیمت:</b> {p.price:,.0f} تومان\n"
            response_text += f"  <b>موجودی:</b> {p.quantity}\n\n"

    await message.answer(response_text)
