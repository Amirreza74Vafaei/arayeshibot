import sys
import os
from sqlalchemy.orm import Session

# Add the project root to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import SessionLocal, engine, Base
from src.db.models import Category, Product

def seed_database():
    """
    Populates the database with initial data for categories and products.
    """
    print("Seeding database...")

    # Create a new database session
    db: Session = SessionLocal()

    try:
        # Drop all tables (for a clean seed) and recreate them
        print("Dropping and recreating all tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("Tables created.")

        # --- Create Categories ---
        cat_electronics = Category(title=" کالای دیجیتال ⚡️")
        cat_books = Category(title="کتاب و لوازم تحریر 📚")
        cat_fashion = Category(title="مد و پوشاک 👕")

        db.add_all([cat_electronics, cat_books, cat_fashion])
        db.commit()
        print(f"Created categories: {cat_electronics.title}, {cat_books.title}, {cat_fashion.title}")

        # --- Create Products ---
        products_to_add = [
            Product(
                sku="EL-001", title="گوشی هوشمند مدل X", description="یک گوشی پرچمدار با دوربین عالی.",
                price=25000000, stock=50, category_id=cat_electronics.id
            ),
            Product(
                sku="EL-002", title="لپتاپ گیمینگ سری G", description="لپتاپ قدرتمند برای بازی و کارهای سنگین.",
                price=55000000, stock=20, category_id=cat_electronics.id
            ),
            Product(
                sku="BK-001", title="کتاب کلیدر", description="اثر محمود دولت‌آبادی.",
                price=850000, stock=100, category_id=cat_books.id
            ),
            Product(
                sku="BK-002", title="خودنویس مدل لوکس", description="یک خودنویس زیبا و روان.",
                price=1200000, stock=200, category_id=cat_books.id
            ),
            Product(
                sku="FA-001", title="تیشرت نخی ساده", description="تیشرت با کیفیت در رنگ‌های متنوع.",
                price=450000, stock=500, category_id=cat_fashion.id
            ),
            Product(
                sku="FA-002", title="کفش ورزشی مدل Run", description="مناسب برای دویدن و ورزش.",
                price=2300000, stock=150, category_id=cat_fashion.id
            ),
        ]

        db.add_all(products_to_add)
        db.commit()
        print(f"Added {len(products_to_add)} products to the database.")

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    seed_database()
