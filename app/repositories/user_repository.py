from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data: dict):
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def verify_user_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


def update_profile_picture(db: Session, user_id: int, object_name: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    user.profile_picture = object_name
    db.commit()
    db.refresh(user)
    return user


def get_user_by_google_id(db: Session, google_id: str):
    return db.query(User).filter(User.google_id == google_id).first()


def link_google_account(db: Session, user_id: int, google_id: str):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.google_id = google_id
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


def get_user_by_github_id(db: Session, github_id: str):
    return db.query(User).filter(User.github_id == github_id).first()


def link_github_account(db: Session, user_id: int, github_id: str):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.github_id = github_id
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


def get_users_paginated(
    db: Session,
    search: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
    page: int = 1,
    limit: int = 10
):
    """
    Search, filter, and paginate users for the admin panel.
    """
    query = db.query(User)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term),
                User.phone_number.ilike(search_term),
                User.city.ilike(search_term)
            )
        )

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)

    total = query.count()
    users = (
        query.order_by(User.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return users, total


def update_user_status(db: Session, user_id: int, is_active: bool):
    """
    Enable or disable a user account.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
