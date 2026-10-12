# repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models.user_model import UserModel

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> UserModel | None:
        """Retrieves a single agent record by their unique username."""
        result = await self.db.execute(select(UserModel).where(UserModel.username == username))
        return result.scalars().first()

    async def create_user(self, username: str, hashed_password: str) -> UserModel:
        """Inserts a brand new agent credentials record into PostgreSQL."""
        new_user = UserModel(username=username, hashed_password=hashed_password)
        self.db.add(new_user)
        return new_user

    # --- NEW CRUD OPERATIONS ---
    async def get_all_users(self) -> list[UserModel]:
        """READ: Retrieves all users registered in the database."""
        result = await self.db.execute(select(UserModel).order_by(UserModel.id))
        return list(result.scalars().all())

    async def update_username(self, user_id: int, new_username: str) -> bool:
        """UPDATE: Modifies an existing user's username."""
        result = await self.db.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalars().first()
        if user:
            user.username = new_username
            return True
        return False

    async def delete_user(self, user_id: int) -> bool:
        """DELETE: Removes an agent completely from the system."""
        result = await self.db.execute(delete(UserModel).where(UserModel.id == user_id))
        return result.rowcount > 0
