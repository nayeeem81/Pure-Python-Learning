# api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
# Import database
from data.database import get_db
from repositories.user_repository import UserRepository
# Import your new validation structures
from schemas import UserRegister, UserResponse, Token 
# api/endpoints.py
# Import security
from security.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_user  # <--- ADD THIS LINE
)

from schemas.user_schema import UserRegister, UserResponse, Token


router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Registers a new agent safely validated through the Schema framework."""
    user_repo = UserRepository(db)
    
    # 1. Check if user already exists
    existing_user = await user_repo.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered"
        )
    
    # 2. Hash and save via repository layer
    hashed = get_password_hash(user_data.password)
    new_user = await user_repo.create_user(username=user_data.username, hashed_password=hashed)
    
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: AsyncSession = Depends(get_db)
):
    """Authenticates credentials and generates a secure schema-validated Token."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ... keep your existing /register and /token endpoints here ...

@router.get("/users", response_model=list[UserResponse])
async def read_all_users(
    current_user: Annotated[str, Depends(get_current_user)], 
    db: AsyncSession = Depends(get_db)
):
    """READ: Protected route to fetch all users."""
    user_repo = UserRepository(db)
    return await user_repo.get_all_users()

@router.put("/users/{user_id}")
async def update_user(
    user_id: int, 
    payload: dict,
    current_user: Annotated[str, Depends(get_current_user)], 
    db: AsyncSession = Depends(get_db)
):
    """UPDATE: Protected route to modify an agent's username."""
    new_name = payload.get("username", "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
        
    user_repo = UserRepository(db)
    success = await user_repo.update_username(user_id, new_name)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "updated"}

@router.delete("/users/{user_id}")
async def delete_user_by_id(
    user_id: int,
    current_user: Annotated[str, Depends(get_current_user)], 
    db: AsyncSession = Depends(get_db)
):
    """DELETE: Protected route to purge an agent profile."""
    user_repo = UserRepository(db)
    success = await user_repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted"}