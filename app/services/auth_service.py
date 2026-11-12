from sqlalchemy.orm import Session
from app.core.security import verify_email_verification_token
from app.repositories.user_repository import verify_user_email
from app.core.security import (hash_password,verify_password,create_access_token)

from app.repositories.user_repository import get_user_by_email
from app.repositories.user_repository import (get_user_by_email ,create_user)

from app.core.security import create_email_verification_token
from app.services.email_service import send_verification_email
from app.services.google_auth_service import verify_google_token
from app.services.facebook_auth_service import verify_facebook_token

from app.repositories.user_repository import (
    get_user_by_google_id,
    link_google_account,
    get_user_by_facebook_id,
    link_facebook_account,
)

class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class EmailNotVerifiedError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    """Raised when an email address already exists in the database."""
    pass    









def register_user(db: Session, user_data):
    existing_user  =get_user_by_email(db, user_data.email)
    
    if existing_user:
        raise EmailAlreadyExistsError("Email already registered")
    
    hashed_password =hash_password(user_data.password)
    new_user_data ={
        "name": user_data.name,
        "email":user_data.email,
        "hashed_password":hashed_password,
        "role":"customer",
        "is_verified": False

    }

    new_user = create_user(db, new_user_data)

    # Generate email verification token
    verification_token = create_email_verification_token(
        new_user.email
    )

    # Send verification email (log error instead of failing transaction if SMTP is unavailable)
    try:
        send_verification_email(
            new_user.email,
            verification_token
        )
    except Exception as email_err:
        print(f"Warning: Failed to dispatch verification email to {new_user.email}: {email_err}")

    return new_user




def login_user(db: Session, user_data):

    # Step 1: Find user by email

    user = get_user_by_email(
        db,
        user_data.email
    )

    # Step 2: Check whether user exists

    if not user:
        raise InvalidCredentialsError(
            "Invalid email or password"
        )

    # Step 3: Verify password

    # Step 3: Check whether the user has a password

    if not user.hashed_password:
     raise InvalidCredentialsError(
        "This account uses Google login. Please sign in with Google."
    )

    # Step 4: Verify password

    is_password_valid = verify_password(
    user_data.password,
    user.hashed_password
    )

    if not is_password_valid:
        raise InvalidCredentialsError(
            "Invalid email or password"
        )

    # Step 4: Check whether account is active

    if not user.is_active:
        raise InactiveUserError(
            "Your account is inactive"
        )

    if not user.is_verified:
        raise EmailNotVerifiedError(
            "Please verify your email before logging in"
        )


    # Step 5: Generate JWT access token

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def facebook_login(db: Session, token: str):
    """
    Authenticates a user via Facebook Graph API.
    Supports seamless account linking by email.
    """
    # Step 1: Verify Facebook Access Token and fetch user info
    fb_user = verify_facebook_token(token)

    facebook_id = fb_user["facebook_id"]
    email = fb_user["email"]
    name = fb_user.get("name") or "Facebook User"

    # Step 2: Find user by Facebook ID
    user = get_user_by_facebook_id(db, facebook_id)

    if not user:
        # Step 3: Check whether this email already belongs to an existing account
        existing_user = get_user_by_email(db, email)

        if existing_user:
            # Merge: link Facebook account to existing user
            user = link_facebook_account(db, existing_user.id, facebook_id)
        else:
            # Step 4: Create new customer
            user_data = {
                "name": name,
                "email": email,
                "hashed_password": None,
                "facebook_id": facebook_id,
                "role": "customer",
                "is_active": True,
                "is_verified": True
            }
            user = create_user(db, user_data)

    # Step 5: Check whether account is active
    if not user.is_active:
        raise InactiveUserError("Your account is inactive")

    # Step 6: Generate application JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



def verify_email(db: Session, token: str):
    email = verify_email_verification_token(token)

    user = verify_user_email(db, email)

    if not user:
        raise ValueError("User not found")

    return user




def google_login(db: Session, token: str):

    # Step 1: Verify the Google ID token
    google_user = verify_google_token(token)

    google_id = google_user["google_id"]
    email = google_user["email"]
    name = google_user.get("name") or email.split("@")[0]

    # Step 2: Find an existing user using Google's unique ID
    user = get_user_by_google_id(db, google_id)

    if not user:

        # Step 3: Check whether this email already belongs to an account
        existing_user = get_user_by_email(db, email)

        if existing_user:
            # Merge: link Google account to existing user without data loss
            user = link_google_account(db, existing_user.id, google_id)
        else:
            # Step 4: Create a new customer
            user_data = {
                "name": name,
                "email": email,
                "hashed_password": None,
                "google_id": google_id,
                "role": "customer",
                "is_active": True,
                "is_verified": True
            }

            user = create_user(db, user_data)

    # Step 5: Check whether the account is active
    if not user.is_active:
        raise InactiveUserError(
            "Your account is inactive"
        )

    # Step 6: Generate our application's JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def facebook_login(db: Session, token: str):
    """
    Authenticates a user via Facebook Graph API.
    Supports seamless account linking by email.
    """
    # Step 1: Verify Facebook Access Token and fetch user info
    fb_user = verify_facebook_token(token)

    facebook_id = fb_user["facebook_id"]
    email = fb_user["email"]
    name = fb_user.get("name") or "Facebook User"

    # Step 2: Find user by Facebook ID
    user = get_user_by_facebook_id(db, facebook_id)

    if not user:
        # Step 3: Check whether this email already belongs to an existing account
        existing_user = get_user_by_email(db, email)

        if existing_user:
            # Merge: link Facebook account to existing user
            user = link_facebook_account(db, existing_user.id, facebook_id)
        else:
            # Step 4: Create new customer
            user_data = {
                "name": name,
                "email": email,
                "hashed_password": None,
                "facebook_id": facebook_id,
                "role": "customer",
                "is_active": True,
                "is_verified": True
            }
            user = create_user(db, user_data)

    # Step 5: Check whether account is active
    if not user.is_active:
        raise InactiveUserError("Your account is inactive")

    # Step 6: Generate application JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



