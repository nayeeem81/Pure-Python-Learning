import os

class AppConfig:
    # Configuration overrides (Ideally load these from config.py)
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_AGENT_KEY_DONT_SHARE")
    ALGORITHM = "HS256"

    # 1. Server Configuration
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    APP_ENV = os.getenv("APP_ENV", "development")

    # 2. Desktop UI Configuration (Tkinter Canvas)
    WINDOW_TITLE = "Agent Secure Desktop Platform"
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    CANVAS_BG_COLOR = "#1e1e1e"  # Dark theme hex code

    @classmethod
    def is_development(cls) -> bool:
        return cls.APP_ENV.lower() == "development"

# Global configuration instance
config = AppConfig()
