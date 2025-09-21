# -*- coding: utf-8 -*-

from aiogram import Router, types, F
from aiogram.filters import Command
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud
from keyboards import inline as inline_kb
from messages import (
    CATEGORIES_PROMPT,
    PRODUCTS_IN_CATEGORY_PROMPT,
    PRODUCT_DETAILS,
    NOT_IMPLEMENTED,
)

router = Router()

# --- 1. Handler for "🗂 دسته‌بندی‌ها" button ---
@router.message(F.text == "🗂 دسته‌بندی‌ها")
async def show_categories(message: types.Message):
    """
    Handles the 'Categories' button click. Fetches categories from the DB
    and displays them as an inline keyboard.
    """
    with get_db() as db:
        categories = crud.get_categories(db)
        if not categories:
            await message.answer("در حال حاضر هیچ دسته‌بندی‌ای وجود ندارد.")
            return

        keyboard = inline_kb.categories_keyboard(categories)
        await message.answer(CATEGORIES_PROMPT, reply_markup=keyboard)

# --- 2. Callback handler for selecting a category ---
@router.callback_query(F.data.startswith("select_category_"))
async def show_products_in_category(callback: types.CallbackQuery):
    """
    Handles a category selection from the inline keyboard.
    Fetches and displays products for the selected category.
    """
    category_id = int(callback.data.split("_")[2])
    with get_db() as db:
        category = crud.get_category(db, category_id)
        if not category:
            await callback.answer("دسته‌بندی یافت نشد.", show_alert=True)
            return

        products = crud.get_products_by_category(db, category_id)
        if not products:
            await callback.message.edit_text(
                f"در دسته **{category.name}** هنوز محصولی وجود ندارد.",
                reply_markup=inline_kb.products_keyboard([], category_id) # Show back button
            )
            return

        keyboard = inline_kb.products_keyboard(products, category_id)
        await callback.message.edit_text(
            PRODUCTS_IN_CATEGORY_PROMPT.format(category_name=category.name),
            reply_markup=keyboard
        )
    await callback.answer()

# --- 3. Callback handler for viewing a product's details ---
@router.callback_query(F.data.startswith("view_product_"))
async def show_product_details(callback: types.CallbackQuery):
    """
    Handles a product selection. Displays detailed information about the product.
    """
    product_id = int(callback.data.split("_")[2])
    with get_db() as db:
        product = crud.get_product(db, product_id)
        if not product:
            await callback.answer("محصول یافت نشد.", show_alert=True)
            return

        text = PRODUCT_DETAILS.format(
            name=product.name,
            description=product.description or "توضیحات موجود نیست.",
            price=f"{product.price:,.0f}", # Format price with commas
            quantity=product.quantity
        )
        keyboard = inline_kb.product_details_keyboard(product.id, product.category_id)

        # Check if the product has an image
        image_path = f"assets/images/{product.image_path}"
        try:
            # We try to send a photo with caption. If it fails, we send text.
            await callback.message.answer_photo(
                photo=types.FSInputFile(image_path),
                caption=text,
                reply_markup=keyboard
            )
            # Delete the old message (the product list)
            await callback.message.delete()
        except Exception:
            # If there's an error (e.g., file not found), just edit the message text
            await callback.message.edit_text(text, reply_markup=keyboard)

    await callback.answer()

# --- 4. Callback handler for going back to the category list ---
@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery):
    """
    Handles the 'Back to Categories' button.
    """
    with get_db() as db:
        categories = crud.get_categories(db)
        keyboard = inline_kb.categories_keyboard(categories)
        await callback.message.edit_text(CATEGORIES_PROMPT, reply_markup=keyboard)
    await callback.answer()

# --- 5. Callback handler for going back to the product list ---
@router.callback_query(F.data.startswith("back_to_products_"))
async def back_to_products(callback: types.CallbackQuery):
    """
    Handles the 'Back to Product List' button.
    """
    category_id = int(callback.data.split("_")[3])
    # This is essentially the same logic as show_products_in_category
    await show_products_in_category(callback)
    # We edit the message, so we need to delete the photo message if it exists
    # A simple way is to just delete the current message if it has a photo
    if callback.message.photo:
        await callback.message.delete()
    await callback.answer()
