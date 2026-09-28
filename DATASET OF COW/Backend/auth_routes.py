from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_from_token,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# SECURITY
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# REQUEST MODELS
# ============================================================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# REGISTER
# ============================================================

@router.post("/register")
def register(request: RegisterRequest):

    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 6 characters."
        )

    user = create_user(
        name=request.name,
        email=request.email,
        password=request.password,
        phone=request.phone or "",
    )

    return {
        "success": True,
        "message": "User registered successfully.",
        "user": user,
    }


# ============================================================
# LOGIN
# ============================================================
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_access_token(
        user_id=user["user_id"],
        email=user["email"],
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "phone": user.get("phone", ""),
        },
    }

# ============================================================
# CURRENT USER
# ============================================================

@router.get("/me")
def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    user = get_user_from_token(token)

    return {
        "success": True,
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "phone": user.get("phone", ""),
            "status": user.get("status", "active"),
            "created_at": user.get("created_at"),
        },
    }