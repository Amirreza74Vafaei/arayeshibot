from aiogram import Router, types, F
from sqlalchemy.orm import Session

from src.db import crud, session as db_session
from src.bot.keyboards.inline_keyboards import get_categories_keyboard

products_router = Router()

@products_router.message(F.text == "🛍️ محصولات")
async def show_categories(message: types.Message):
    """
    Handles the 'Products' button click.
    Fetches product categories from the DB and displays them as an inline keyboard.
    """
    db: Session = next(db_session.get_db())
    categories = crud.get_categories(db)
    db.close()

    if not categories:
        await message.answer("در حال حاضر هیچ محصولی برای نمایش وجود ندارد.")
        return

    keyboard = get_categories_keyboard(categories)
    await message.answer("لطفاً یک دسته‌بندی را انتخاب کنید:", reply_markup=keyboard)

from src.bot.keyboards.inline_keyboards import get_products_keyboard

PAGE_SIZE = 6

@products_router.callback_query(F.data.startswith("category:"))
async def show_product_list(callback_query: types.CallbackQuery):
    """
    Handles the category selection from the inline keyboard.
    Displays a paginated list of products for the selected category.
    """
    # Extract category_id and page from callback_data
    try:
        _, category_id_str, page_str = callback_query.data.split(":")
        category_id = int(category_id_str)
        page = int(page_str)
    except (ValueError, IndexError):
        await callback_query.answer("خطای اطلاعات دریافتی.", show_alert=True)
        return

    db: Session = next(db_session.get_db())
    products = crud.get_products_by_category(db, category_id=category_id, page=page, page_size=PAGE_SIZE)
    total_products = crud.count_products_by_category(db, category_id=category_id)
    db.close()

    if not products:
        await callback_query.answer("محصولی در این دسته‌بندی یافت نشد.", show_alert=True)
        return

    keyboard = get_products_keyboard(
        products=products,
        total_products=total_products,
        category_id=category_id,
        page=page,
        page_size=PAGE_SIZE
    )

    # Edit the message to show the product list
    await callback_query.message.edit_text(
        "محصول مورد نظر خود را انتخاب کنید:",
        reply_markup=keyboard
    )
    await callback_query.answer() # Acknowledge the callback

@products_router.callback_query(F.data == "back_to_categories")
async def back_to_category_list(callback_query: types.CallbackQuery):
    """
    Handles the 'Back to categories' button click.
    """
    db: Session = next(db_session.get_db())
    categories = crud.get_categories(db)
    db.close()

    keyboard = get_categories_keyboard(categories)
    await callback_query.message.edit_text(
        "لطفاً یک دسته‌بندی را انتخاب کنید:",
        reply_markup=keyboard
    )
    await callback_query.answer()

from src.bot.keyboards.inline_keyboards import get_product_detail_keyboard

@products_router.callback_query(F.data.startswith("product:"))
async def show_product_detail(callback_query: types.CallbackQuery):
    """
    Handles the product selection from the product list.
    Displays detailed information about the selected product.
    """
    try:
        _, product_id_str = callback_query.data.split(":")
        product_id = int(product_id_str)
    except (ValueError, IndexError):
        await callback_query.answer("خطای اطلاعات دریافتی.", show_alert=True)
        return

    db: Session = next(db_session.get_db())
    product = crud.get_product_by_id(db, product_id=product_id)
    db.close()

    if not product:
        await callback_query.answer("محصول مورد نظر یافت نشد.", show_alert=True)
        return

    # Format the product detail message
    # Using bold for titles and code for SKU
    caption = (
        f"<b>{product.title}</b>\n\n"
        f"{product.description}\n\n"
        f"<i>قیمت:</i> <b>{product.price:,.0f} تومان</b>\n"
        f"<code>کد محصول: {product.sku}</code>"
    )

    keyboard = get_product_detail_keyboard(product)

    # In a real scenario, you'd send a photo with this caption
    # For now, we'll just edit the text.
    await callback_query.message.edit_text(
        text=caption,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()
