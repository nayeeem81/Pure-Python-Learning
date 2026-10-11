# schemas/user_schema.py
from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    """Validates the incoming payload when creating a new agent account."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique identifier for the agent")
    password: str = Field(..., min_length=6, description="Secure account password")

class UserResponse(BaseModel):
    """Controls the exact fields serialized and returned back to the desktop client."""
    username: str

    class Config:
        # Allows Pydantic to read data directly from your SQLAlchemy Model instances
        from_attributes = True

class Token(BaseModel):
    """Validates structure for OAuth2 compliant authorization responses."""
    access_token: str
    token_type: str
