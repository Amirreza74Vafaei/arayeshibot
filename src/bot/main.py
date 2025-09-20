import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.core.config import settings
from src.bot.handlers.start import start_router
from src.bot.handlers.products import products_router

# Load environment variables from .env file at the root
load_dotenv()

async def main() -> None:
    """
    Initializes and starts the Telegram bot.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Initialize Bot and Dispatcher
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # Include routers
    dp.include_router(start_router)
    dp.include_router(products_router)

    from src.bot.handlers.cart import cart_router
    dp.include_router(cart_router)

    from src.bot.handlers.order import order_router
    dp.include_router(order_router)

    # Start polling
    logging.info("Starting bot polling...")
    # To prevent conflicts with other running bots, we can skip updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
