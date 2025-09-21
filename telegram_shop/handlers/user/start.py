# -*- coding: utf-8 -*-

from aiogram import Router, types
from aiogram.filters import CommandStart

from messages import WELCOME_MESSAGE
from keyboards.reply import main_menu_keyboard
from db.database import get_db
from db.models import User
from sqlalchemy.orm import Session

router = Router()

@router.message(CommandStart())
async def command_start(message: types.Message):
    """
    Handler for the /start command.
    Greets the user, registers them in the database if they are new,
    and shows the main menu.
    """
    user = message.from_user

    # Add or update user in the database
    with get_db() as db:
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            new_user = User(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                language_code=user.language_code
            )
            db.add(new_user)
            db.commit()

    await message.answer(
        text=WELCOME_MESSAGE,
        reply_markup=main_menu_keyboard()
    )
