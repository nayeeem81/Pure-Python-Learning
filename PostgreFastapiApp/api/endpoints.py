# api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
# Import database
from data.database import get_db
from repositories.user_repository import UserRepository
# Import security
from security.auth import verify_password, get_password_hash, create_access_token
# Import your new validation structures
from schemas import UserRegister, UserResponse, Token 

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
    
    # The endpoint safely filters out the password hash because response_model=UserResponse
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
