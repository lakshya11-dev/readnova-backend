from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.schemas.user_login import UserLogin
from app.schemas.token_response import TokenResponse
from app.schemas.user_register import UserRegister
from app.schemas.user_response import UserResponse
from app.services.auth_service import verify_email
from app.schemas.google_login import GoogleLoginRequest
from app.services.auth_service import google_login


from app.services.auth_service import (
    login_user,
    InvalidCredentialsError,
    InactiveUserError,
    EmailNotVerifiedError
)

from app.services.auth_service import (
    register_user,
    EmailAlreadyExistsError)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(user_data: UserRegister,db: Session = Depends(get_db)):

    try:

        new_user = register_user(db,user_data)
        return new_user

    except EmailAlreadyExistsError:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )



@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    try:

        token = login_user(
            db,
            user_data
        )

        return token

    except InvalidCredentialsError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    except InactiveUserError:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive"
        )

    except EmailNotVerifiedError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error)
        )



@router.get("/me",response_model=UserResponse)
def get_my_profile(current_user = Depends(get_current_user)):
    return current_user



@router.get("/verify-email")
def verify_email_endpoint(token: str,db: Session = Depends(get_db)):
    try:
        user = verify_email(db, token)

        return {
            "message": "Email verified successfully",
            "email": user.email,
            "is_verified": user.is_verified
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

@router.post("/google", response_model=TokenResponse)
def google_login_endpoint(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    try:
        result = google_login(db, payload.id_token)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )

    except InactiveUserError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error)
        )
