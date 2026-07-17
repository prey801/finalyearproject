from fastapi import APIRouter, Depends
from backend.database.models import User as DBUser
from backend.schemas.auth import User as UserSchema
from backend.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Note: /register and /token endpoints have been removed.
# Authentication is now fully managed by Supabase.

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: DBUser = Depends(get_current_active_user)):
    return current_user
