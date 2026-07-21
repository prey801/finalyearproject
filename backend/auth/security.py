import os
from passlib.context import CryptContext
import jwt
from jwt import PyJWKClient

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
_raw_secret = os.environ.get("SUPABASE_JWT_SECRET")

if not _raw_secret and not SUPABASE_URL:
    if os.environ.get("ENV", "development") == "production":
        raise ValueError("SECURITY VIOLATION: SUPABASE_JWT_SECRET or SUPABASE_URL must be set in production mode!")

    import logging
    logging.getLogger(__name__).warning(
        "Neither SUPABASE_JWT_SECRET nor SUPABASE_URL is set. "
        "Token verification will fail for real Supabase sessions."
    )

# Fallback keeps the dev bypass working (no token = test_clinician user)
SUPABASE_JWT_SECRET = _raw_secret or "unset-dev-secret"
ALGORITHM = "HS256"

# Modern Supabase projects sign session tokens asymmetrically (ES256) and
# publish their public keys via JWKS — no shared secret needed or available.
# Older/self-hosted projects still sign with a shared HS256 secret
# (SUPABASE_JWT_SECRET). PyJWKClient lazily fetches + caches keys by `kid`.
_jwks_client = (
    PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json", cache_keys=True)
    if SUPABASE_URL else None
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_supabase_token(token: str):
    """Verifies a Supabase JWT and returns the decoded payload.

    Tries JWKS (asymmetric, current Supabase default) first, then falls
    back to the legacy shared HS256 secret if one is configured.
    """
    if _jwks_client is not None:
        try:
            signing_key = _jwks_client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],
                options={"verify_aud": False},
            )
        except Exception as jwks_error:
            if not _raw_secret:
                raise jwt.PyJWTError(f"JWKS token validation failed: {jwks_error}")
            # fall through to legacy secret-based verification

    try:
        return jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except Exception as e:
        raise jwt.PyJWTError(f"Token validation failed: {str(e)}")
