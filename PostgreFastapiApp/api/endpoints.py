# api/endpoints.py
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Clean subfolder imports
from auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from config import config

router = APIRouter()

# Example local schema/db tracker
mock_user_db = {}

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = mock_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.APP_PORT) # Loaded safely from config
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/agent/secure-data")
async def get_agent_data(current_user: Annotated[str, Depends(get_current_user)]):
    """Secure endpoint accessible only with a valid bearer token."""
    return {
        "status": "success",
        "message": f"Welcome, agent '{current_user}'. Access to classified files granted."
    }
