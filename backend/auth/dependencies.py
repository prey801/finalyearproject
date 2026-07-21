from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from sqlalchemy.orm import Session
from backend.auth.security import verify_supabase_token
from backend.database.session import get_db
from backend.database.models import User
from backend.schemas.auth import TokenData

security = HTTPBearer(auto_error=False)
ENV = os.environ.get("ENV", "development")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        if ENV == "production":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Development fallback bypass
        user = db.query(User).filter(User.username == "test_clinician").first()
        if not user:
            user = User(
                username="test_clinician", 
                email="test@example.com", 
                hashed_password="SUPABASE_MANAGED", 
                full_name="Test Clinician"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_supabase_token(credentials.credentials)
        email = payload.get("email")
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
            
        username = email if email else sub
        
        # Upsert user to keep local DB in sync with Supabase Auth.
        # Only match on email when it's present — email is nullable, and
        # `User.email == None` would otherwise match any other null-email user.
        if email:
            user = db.query(User).filter((User.email == email) | (User.username == username)).first()
        else:
            user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                email=email,
                hashed_password="SUPABASE_MANAGED",
                full_name=payload.get("user_metadata", {}).get("full_name")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return user
    except jwt.PyJWTError as e:
        print(f"JWT Verification error: {e}")
        raise credentials_exception

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
