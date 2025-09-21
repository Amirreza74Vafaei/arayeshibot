import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from utils.logger import setup_logging
from handlers.user import start as user_start_router
from handlers.user import catalog as user_catalog_router
from handlers.user import cart as user_cart_router
from handlers.user import checkout as user_checkout_router
from handlers.user import orders as user_orders_router
from handlers.admin import main as admin_main_router
from handlers.admin import products as admin_products_router
from handlers.admin import orders as admin_orders_router
from handlers.admin import settings as admin_settings_router

# A placeholder for a function to register all routers
# We will build this out as we create more handlers
def register_all_routers(dp: Dispatcher):
    """Registers all routers for the bot."""
    dp.include_router(user_start_router.router)
    dp.include_router(user_catalog_router.router)
    dp.include_router(user_cart_router.router)
    dp.include_router(user_checkout_router.router)
    dp.include_router(user_orders_router.router)

    # Register admin routers
    dp.include_router(admin_main_router.router)
    dp.include_router(admin_products_router.router)
    dp.include_router(admin_orders_router.router)
    dp.include_router(admin_settings_router.router)
    logging.info("Registered all routers.")


async def main():
    """
    The main function that starts the bot.
    """
    # Setup logging
    setup_logging()
    logging.info("Starting bot...")

    # Load environment variables from .env file
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logging.error("BOT_TOKEN not found in .env file. Bot cannot start.")
        return

    # Initialize Bot and Dispatcher
    # Using 'HTML' parse mode for messages
    bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Register all the routers from different modules
    # Register all the routers from different modules
    register_all_routers(dp)

    # Start polling
    # Before starting, we delete any existing webhook to ensure polling works.
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Starting polling...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Critical error during polling: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
    except Exception as e:
        logging.critical(f"Bot failed to start: {e}", exc_info=True)
