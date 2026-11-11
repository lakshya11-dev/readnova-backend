from app.database.connection import settings
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status
from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone



password_hash=PasswordHash.recommended()

def hash_password(password:str)->str:
    return password_hash.hash(password)

def verify_password(plain_password:str , hashed_password:str)->bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token



def verify_access_token(token: str) -> dict:

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidTokenError("Token does not contain subject")

        return payload

    except InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


def create_email_verification_token(email: str) -> str:

    expire = datetime.now(timezone.utc) + timedelta(hours=24)

    payload = {
        "sub": email,
        "purpose": "email_verification",
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token

def verify_email_verification_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("purpose") != "email_verification":
            raise InvalidTokenError("Invalid token purpose")

        email = payload.get("sub")

        if not email:
            raise InvalidTokenError("Email missing from token")

        return email

    except InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification link"
        )