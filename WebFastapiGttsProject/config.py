import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # Loads .env if present
class AppConfig:
	STORAGE_ROOT = Path(r"D:\StudioStorage")   
	GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6Iphno3nu83n5ChGbDBL8xYxnwVGGuBAAFSnlxSCVL3Ig")

	SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_AGENT_KEY_DONT_SHARE")
	ALGORITHM = "HS256"
	APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
	APP_PORT = int(os.getenv("APP_PORT", "8000"))
	APP_ENV = os.getenv("APP_ENV", "development")
	DB_USER = os.getenv("DB_USER", "postgres")
	DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
	DB_HOST = os.getenv("DB_HOST", "localhost")
	DB_PORT = os.getenv("DB_PORT", "5432")
	DB_NAME = os.getenv("DB_NAME", "gttstunevolume_db")

	@property
	def CHAT_AUDIO_DIR(self) -> Path:
		folder = self.STORAGE_ROOT / "chat_audio"
		folder.mkdir(parents=True, exist_ok=True)
		return folder

	@property
	def DATABASE_URL(self) -> str:
		return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

	@classmethod
	def is_development(cls) -> bool:
		return cls.APP_ENV.lower() == "development"

config = AppConfig()
