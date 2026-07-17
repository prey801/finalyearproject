from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from backend.auth.security import verify_supabase_token
from backend.database.session import get_db
from backend.database.models import User
from backend.schemas.auth import TokenData

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
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
        
        # Upsert user to keep local DB in sync with Supabase Auth
        user = db.query(User).filter((User.email == email) | (User.username == username)).first()
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
