
from sqlalchemy.orm import Session

from app.models.user import User


def get_address(db: Session, user_id: int):
    # Find the customer using their ID
    user = db.query(User).filter(User.id == user_id).first()

    # Return None if the customer does not exist
    if not user:
        return None

    # Return the customer record containing the address fields
    return user


def save_address(db: Session, user_id: int, address_data: dict):
    # Find the customer
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    # Save the submitted address fields
    for field, value in address_data.items():
        setattr(user, field, value)

    # Commit changes to PostgreSQL
    db.commit()

    # Refresh the customer record
    db.refresh(user)

    return user


def update_address(db: Session, user_id: int, update_data: dict):
    # Find the customer
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    # Update only the fields provided
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user
