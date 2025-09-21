# -*- coding: utf-8 -*-

# This file contains all the messages for the bot in Farsi.
# Using a separate file for messages makes it easier to manage and translate.

# --- Welcome and Main Menu ---
WELCOME_MESSAGE = """
سلام 👋
به فروشگاه ما خوش اومدی!

🛍️ برای مشاهده دسته‌ها روی دکمه "دسته‌بندی‌ها" کلیک کن یا از جستجو استفاده کن.

💰 تمام پرداخت‌ها به صورت **درب منزل** (COD) انجام می‌شه.
"""

# --- User Flow Messages ---
CATEGORIES_PROMPT = "یک دسته را انتخاب کنید:"
PRODUCTS_IN_CATEGORY_PROMPT = "محصولات دسته **{category_name}**:"
PRODUCT_DETAILS = """
<b>{name}</b>

{description}

<b>قیمت:</b> {price} تومان
<b>موجودی:</b> {quantity} عدد

برای افزودن به سبد خرید، تعداد را مشخص و دکمه زیر را فشار دهید.
"""

# --- Cart Messages ---
CART_EMPTY = "سبد خرید شما خالی است."
CART_HEADER = "🛒 **سبد خرید شما**\n\n"
CART_ITEM_LINE = "{index}. <b>{name}</b>\n   تعداد: {quantity} عدد × {price} تومان = {total_price} تومان\n"
CART_FOOTER = "\n\nجمع کل: **{total} تومان**"


# --- Checkout Messages ---
CHECKOUT_PROMPT_NAME = "لطفاً نام کامل گیرنده را وارد کنید:"
CHECKOUT_PROMPT_PHONE = "لطفاً شماره تماس خود را وارد کنید (مثال: 09123456789):"
CHECKOUT_PROMPT_ADDRESS = "لطفاً آدرس دقیق خود را برای تحویل وارد کنید:"
CHECKOUT_INVALID_PHONE = "فرمت شماره تماس نامعتبر است. لطفاً دوباره تلاش کنید."
CHECKOUT_CONFIRMATION = """
لطفاً اطلاعات سفارش خود را تأیید کنید:

**گیرنده:** {name}
**تلفن:** {phone}
**آدرس:** {address}

**خلاصه سفارش:**
{summary}
**هزینه ارسال:** {shipping_cost} تومان
**مبلغ نهایی (پرداخت درب منزل):** {final_total} تومان

در صورت صحت اطلاعات، دکمه "✅ تأیید و ثبت نهایی" را بزنید.
"""
ORDER_SUCCESS_USER = """
✅ مرسی! سفارش شما با شناسه <b>{order_uid}</b> با موفقیت ثبت شد.

پرداخت هنگام تحویل انجام می‌شود.
ما در اسرع وقت سفارش را بررسی کرده و وضعیت آن را به شما اطلاع خواهیم داد.
"""

# --- Admin Messages ---
NEW_ORDER_ADMIN_NOTIFICATION = """
🚨 **سفارش جدید ثبت شد!** 🚨

<b>شناسه سفارش:</b> {order_uid}
<b>کاربر:</b> {user_link} (ID: {user_id})
<b>نام گیرنده:</b> {recipient_name}
<b>تلفن:</b> {recipient_phone}
<b>آدرس:</b>
{shipping_address}

<b>آیتم‌های سفارش:</b>
{items_summary}
<b>جمع مبلغ محصولات:</b> {total_amount} تومان
<b>هزینه ارسال:</b> {shipping_cost} تومان
<b>مبلغ نهایی قابل پرداخت:</b> {final_total} تومان

برای مدیریت سفارش از دستورات زیر استفاده کنید:
`/view_order {order_uid}`
`/accept_order {order_uid}`
"""

# --- General Error Messages ---
GENERAL_ERROR = "خطایی رخ داده است. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."
NOT_IMPLEMENTED = "این قابلیت هنوز پیاده‌سازی نشده است."
