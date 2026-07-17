import os
from passlib.context import CryptContext
import jwt

# Replace the old DEV_SECRET with Supabase integration
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "bde26b97-870b-4434-91c4-fa27bebfabc8")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_supabase_token(token: str):
    """Verifies a Supabase JWT and returns the decoded payload."""
    try:
        # Supabase uses HS256 with the JWT secret
        # They don't require audience validation by default unless explicitly configured
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=[ALGORITHM],
            options={"verify_aud": False}
        )
        return payload
    except Exception as e:
        raise jwt.PyJWTError(f"Token validation failed: {str(e)}")
