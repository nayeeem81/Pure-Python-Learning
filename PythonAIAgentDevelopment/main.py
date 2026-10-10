import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import exceptions, encode as jwt_encode, decode as jwt_decode
from passlib.context import CryptContext
from pydantic import BaseModel

# 1. Configuration Settings
SECRET_KEY = "SUPER_SECRET_AGENT_KEY_CHANGE_THIS_IN_PRODUCTION" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 2. Security Utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# This tells FastAPI where to look for the token (the "/token" endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="AI Agent Authentication Server")

# 3. Mock In-Memory Database (Replace with PostgreSQL/MongoDB in production)
mock_user_db = {}

# 4. Pydantic Schemas for Validation
class UserRegister(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 5. Helper Functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """Dependency injection function to guard secure routes."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except exceptions.PyJWTError:
        raise credentials_exception
        
    if username not in mock_user_db:
        raise credentials_exception
    return username

# 6. API Endpoints

@app.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserRegister):
    """Registers a new agent/user and hashes their password."""
    if user.username in mock_user_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    mock_user_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed_password
    }
    return {"username": user.username}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Standard OAuth2 compatible token login. Returns a JWT access token."""
    user = mock_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/agent/secure-data")
async def get_agent_data(current_user: Annotated[str, Depends(get_current_user)]):
    """A protected endpoint that only authenticated agents/users can access."""
    return {
        "status": "success",
        "message": f"Welcome, agent '{current_user}'. Access to classified agent files granted.",
        "secret_payload": "Data-42-Agentic-System-Active"
    }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)