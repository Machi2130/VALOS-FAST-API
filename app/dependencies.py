
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app import schemas  # ✅ Import schemas here
from app.database import get_db
from app.models.user import User
from app.config import get_settings

settings = get_settings()

# Password hashing - CORRECT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme - FIXED tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/")

def get_password_hash(password: str) -> str:
    """Hash password - CORRECT implementation"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - CORRECT implementation"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token with embedded user data.
    This avoids DB lookup on every request.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_access_token_with_user(user: "User", expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT with embedded user data to avoid DB lookup on every request.
    """
    to_encode = {
        "sub": user.username,
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

class CachedUser:
    """
    Lightweight user object created from JWT payload.
    Avoids DB query on every request.
    """
    def __init__(self, payload: dict):
        self.id = payload.get("user_id")
        self.username = payload.get("sub")
        self.email = payload.get("email")
        self.full_name = payload.get("full_name")
        self.is_active = payload.get("is_active", True)
        self.is_superuser = payload.get("is_superuser", False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> CachedUser:
    """
    Get current user from JWT token WITHOUT hitting the database.
    User data is embedded in the token itself.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise credentials_exception
        
        return CachedUser(payload)
    except JWTError:
        raise credentials_exception

async def get_current_active_user(
    current_user: CachedUser = Depends(get_current_user)
) -> CachedUser:
    """Ensure user is active (no DB query needed)"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
