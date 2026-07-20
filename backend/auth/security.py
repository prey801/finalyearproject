import os
from passlib.context import CryptContext
import jwt

_raw_secret = os.environ.get("SUPABASE_JWT_SECRET")
if not _raw_secret:
    if os.environ.get("ENV", "development") == "production":
        raise ValueError("SECURITY VIOLATION: SUPABASE_JWT_SECRET must be set in production mode!")
        
    import logging
    logging.getLogger(__name__).warning(
        "SUPABASE_JWT_SECRET env var is not set. "
        "Token verification will fail for real Supabase sessions. "
        "Set it to the JWT secret from your Supabase project settings."
    )
    # Fallback keeps the dev bypass working (no token = test_clinician user)
    _raw_secret = "unset-dev-secret"

SUPABASE_JWT_SECRET = _raw_secret
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
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        return payload
    except Exception as e:
        raise jwt.PyJWTError(f"Token validation failed: {str(e)}")
