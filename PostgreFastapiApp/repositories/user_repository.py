# repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import UserModel

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> UserModel | None:
        """Retrieves a single agent record by their unique username."""
        result = await self.db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalars().first()

    async def create_user(self, username: str, hashed_password: str) -> UserModel:
        """Inserts a brand new agent credentials record into PostgreSQL."""
        new_user = UserModel(username=username, hashed_password=hashed_password)
        self.db.add(new_user)
        # Session saves automatically if using our get_db context manager
        return new_user

