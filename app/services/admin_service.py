import math
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.user_repository import (
    get_users_paginated,
    get_user_by_id,
    update_user_status
)
from app.services.storage_service import generate_file_url


def list_users(
    db: Session,
    search: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
    page: int = 1,
    limit: int = 10
):
    users, total = get_users_paginated(
        db=db,
        search=search,
        role=role,
        is_active=is_active,
        is_verified=is_verified,
        page=page,
        limit=limit
    )

    from app.services.plan_service import get_user_plan_data

    items = []
    for user in users:
        picture_url = None
        if user.profile_picture:
            picture_url = generate_file_url(user.profile_picture)

        plan_info = get_user_plan_data(user.id)

        items.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "phone_number": user.phone_number,
            "city": user.city,
            "state": user.state,
            "country": user.country,
            "postal_code": user.postal_code,
            "latitude": user.latitude,
            "longitude": user.longitude,
            "profile_picture_url": picture_url,
            "plan_name": plan_info.get("plan_name", "Free"),
            "plan_status": plan_info.get("plan_status", "active"),
            "plan_expires_at": plan_info.get("expires_at"),
            "created_at": user.created_at
        })

    total_pages = math.ceil(total / limit) if total > 0 else 1

    return {
        "items": items,
        "users": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


def get_user_details(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    picture_url = None
    if user.profile_picture:
        picture_url = generate_file_url(user.profile_picture)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "phone_number": user.phone_number,
        "address": user.address,
        "city": user.city,
        "state": user.state,
        "country": user.country,
        "postal_code": user.postal_code,
        "latitude": user.latitude,
        "longitude": user.longitude,
        "profile_picture_url": picture_url,
        "created_at": user.created_at
    }


def change_user_status(db: Session, user_id: int, is_active: bool):
    user = update_user_status(db, user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": f"User account has been {'activated' if is_active else 'deactivated'} successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }

