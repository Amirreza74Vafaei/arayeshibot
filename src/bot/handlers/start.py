from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlalchemy.orm import Session

from src.db import crud, session as db_session
from src.bot.keyboards.reply_keyboards import get_main_menu_keyboard
from src.core.config import settings

start_router = Router()

@start_router.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Handler for the /start command.
    Greets the user, creates a database entry for them, and shows the main menu.
    """
    # Create a new database session
    db: Session = next(db_session.get_db())

    # Get or create the user in the database
    user = crud.get_or_create_user(db, telegram_user=message.from_user)

    db.close()

    # Prepare the welcome message
    welcome_message = (
        f"سلام {user.first_name} 👋\n"
        f"به فروشگاه {settings.BRAND_NAME} خوش آمدی!\n\n"
        "برای دیدن محصولات دکمه «محصولات» رو بزن یا از منو استفاده کن."
    )

    # Send the welcome message with the main menu keyboard
    await message.answer(
        welcome_message,
        reply_markup=get_main_menu_keyboard()
    )
