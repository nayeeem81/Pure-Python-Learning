# Global settings (app titles, environment secrets)
import os

class AppConfig:
    # Configuration overrides (Ideally load these from config.py)
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_AGENT_KEY_DONT_SHARE")
    ALGORITHM = "HS256"

    # Server Configuration
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    APP_ENV = os.getenv("APP_ENV", "development")

    # PostgreSQL Database Configuration
    # Replace username, password, localhost, and dbname with your actual system credentials
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "gttstunevolume_db")

    @property
    def DATABASE_URL(self) -> str:
        # We use postgresql+asyncpg for modern asynchronous FastAPI applications
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @classmethod
    def is_development(cls) -> bool:
        return cls.APP_ENV.lower() == "development"

# Global configuration instance
config = AppConfig()
