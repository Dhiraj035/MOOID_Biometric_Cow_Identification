import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from mongodb_service import db


# ============================================================
# ENVIRONMENT
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")

load_dotenv(ENV_FILE)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")


# ============================================================
# MONGODB
# ============================================================

users_collection = db["users"]


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert a plain password into a secure Argon2 hash.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against the stored hash.
    """
    return password_hash.verify(password, hashed_password)


# ============================================================
# USER FUNCTIONS
# ============================================================

def get_user_by_email(email: str):
    """
    Find a user by email address.
    """
    return users_collection.find_one({
        "email": email.lower().strip()
    })


def create_user(
    name: str,
    email: str,
    password: str,
    phone: str = "",
):
    """
    Create a new user in MongoDB.
    """

    email = email.lower().strip()

    # Check duplicate email
    existing_user = get_user_by_email(email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered."
        )

    # Generate user ID
    user_count = users_collection.count_documents({})

    user_id = f"USR{user_count + 1:03d}"

    now = datetime.now(timezone.utc)

    user_document = {
        "user_id": user_id,
        "name": name.strip(),
        "email": email,
        "phone": phone.strip(),
        "password_hash": hash_password(password),
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }

    users_collection.insert_one(user_document)

    return {
        "user_id": user_id,
        "name": name.strip(),
        "email": email,
        "phone": phone.strip(),
    }


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_user(email: str, password: str):
    """
    Verify user email and password.
    """

    user = get_user_by_email(email)

    if not user:
        return None

    if user.get("status") != "active":
        return None

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return None

    return user


# ============================================================
# JWT
# ============================================================

def create_access_token(user_id: str, email: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


def decode_access_token(token: str):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception

        return payload

    except InvalidTokenError:

        raise credentials_exception


# ============================================================
# GET USER FROM TOKEN
# ============================================================

def get_user_from_token(token: str):

    payload = decode_access_token(token)

    user_id = payload["sub"]

    user = users_collection.find_one({
        "user_id": user_id
    })

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if user.get("status") != "active":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    return user