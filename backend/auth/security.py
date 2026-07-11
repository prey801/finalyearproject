import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from typing import Optional

# In production, set this environment variable
DEFAULT_DEV_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_DEV_SECRET)
ENV = os.environ.get("ENV", "development")

if ENV == "production" and SECRET_KEY == DEFAULT_DEV_SECRET:
    raise ValueError("SECURITY VIOLATION: Default fallback SECRET_KEY cannot be used in production mode!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
