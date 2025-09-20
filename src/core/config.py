import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()

class Settings(BaseSettings):
    # Bot Settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    # Database Settings
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "telegram_shop")
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))

    # Using a property allows for dynamic URL creation based on other settings.
    # It also allows for easy switching between database dialects.
    @property
    def DATABASE_URL(self) -> str:
        # If a DB_HOST is provided, assume PostgreSQL. Otherwise, default to a local SQLite DB for development.
        if self.DB_HOST and self.DB_HOST != 'db': # 'db' is the default in .env.example
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            # Default to a local SQLite database file named 'telegram_shop.db' in the project root.
            # This is useful for local development and testing without Docker.
            return "sqlite:///telegram_shop.db"

    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    # JWT Settings for Admin Panel
    ADMIN_JWT_SECRET_KEY: str = os.getenv("ADMIN_JWT_SECRET_KEY", "secret")

    # Application Settings
    ADMIN_TELEGRAM_ID: int = int(os.getenv("ADMIN_TELEGRAM_ID", 0))
    CONTACT_SUPPORT_LINK: str = os.getenv("CONTACT_SUPPORT_LINK", "")
    ABOUT_US_TEXT: str = os.getenv("ABOUT_US_TEXT", "")
    BRAND_NAME: str = os.getenv("BRAND_NAME", "My Shop")

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate the settings
settings = Settings()
