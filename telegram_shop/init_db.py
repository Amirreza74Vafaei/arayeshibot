import logging
import os
import sys

# Add the project root to the Python path
# This allows us to run this script from the project root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram_shop.db.database import SessionLocal, create_tables
from telegram_shop.db.models import Category, Product, Setting
from telegram_shop.db import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_data():
    """
    Seeds the database with some initial data for testing.
    """
    db = SessionLocal()
    try:
        # --- Seed Categories ---
        if db.query(Category).count() == 0:
            logger.info("Seeding categories...")
            cat1 = Category(name="لپ‌تاپ")
            cat2 = Category(name="گوشی هوشمند")
            cat3 = Category(name="لوازم جانبی")
            db.add_all([cat1, cat2, cat3])
            db.commit()
            logger.info("Categories seeded.")
        else:
            logger.info("Categories already exist, skipping seeding.")

        # --- Seed Products ---
        if db.query(Product).count() == 0:
            logger.info("Seeding products...")
            cat1 = db.query(Category).filter_by(name="لپ‌تاپ").one()
            cat2 = db.query(Category).filter_by(name="گوشی هوشمند").one()
            prod1 = Product(
                name="مک‌بوک پرو ۱۴ اینچ",
                description="یک لپ‌تاپ قدرتمند با چیپ M3 Pro.",
                price=85000000.0,
                quantity=10,
                category_id=cat1.id,
                image_path="macbook_pro_14.jpg"
            )
            prod2 = Product(
                name="آیفون ۱۵ پرو",
                description="جدیدترین پرچمدار اپل با بدنه تیتانیومی.",
                price=60000000.0,
                quantity=25,
                category_id=cat2.id,
                image_path="iphone_15_pro.jpg"
            )
            db.add_all([prod1, prod2])
            db.commit()
            logger.info("Products seeded.")
        else:
            logger.info("Products already exist, skipping seeding.")

        # --- Seed Settings ---
        if db.query(Setting).count() == 0:
            logger.info("Seeding initial settings...")
            shipping_cost = Setting(key="shipping_cost", value="25000")
            db.add(shipping_cost)
            db.commit()
            logger.info("Settings seeded.")
        else:
            logger.info("Settings already exist, skipping seeding.")

    except Exception as e:
        logger.error(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Initializing database...")
    # This will create all the tables defined in models.py
    create_tables()
    # This will add some initial data
    seed_data()
    logger.info("Database initialization complete.")
