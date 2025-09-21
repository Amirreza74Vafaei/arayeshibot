# -*- coding: utf-8 -*-

from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject

from filters.is_admin import IsAdmin
from db.database import get_db
from db import crud

router = Router()
router.message.filter(IsAdmin())

@router.message(F.text == "⚙️ تنظیمات")
async def show_settings(message: types.Message):
    """
    Displays the current settings.
    """
    with get_db() as db:
        shipping_cost = crud.get_setting(db, "shipping_cost") or "0"

    text = (
        "<b>تنظیمات فروشگاه</b>\n\n"
        f"<b>هزینه ارسال فعلی:</b> {int(shipping_cost):,.0f} تومان\n\n"
        "برای تغییر هزینه ارسال، از دستور زیر استفاده کنید:\n"
        "<code>/set_shipping_cost 15000</code>"
    )
    await message.answer(text)

@router.message(Command("set_shipping_cost"))
async def set_shipping_cost(message: types.Message, command: CommandObject):
    """
    Command to set the shipping cost.
    Usage: /set_shipping_cost <amount>
    """
    if command.args is None:
        await message.reply("لطفاً مبلغ هزینه ارسال را بعد از دستور وارد کنید.\nمثال: `/set_shipping_cost 15000`")
        return

    try:
        new_cost = int(command.args)
        if new_cost < 0:
            raise ValueError
    except (ValueError, TypeError):
        await message.reply("مبلغ نامعتبر است. لطفاً یک عدد صحیح مثبت وارد کنید.")
        return

    with get_db() as db:
        crud.set_setting(db, "shipping_cost", str(new_cost))

    await message.reply(f"✅ هزینه ارسال با موفقیت به {new_cost:,.0f} تومان تغییر یافت.")
