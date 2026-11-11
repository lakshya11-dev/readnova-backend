
from sqlalchemy.orm import Session

from app.models.user import User


def update_profile(db: Session,user_id: int,update_data: dict):
    # Find the customer using their ID
    user = db.query(User).filter(User.id == user_id).first()

    # Check whether the customer exists
    if not user:
        return None

    # Update only the fields provided by the customer
    for field, value in update_data.items():
        setattr(user, field, value)

    # Save changes to the database
    db.commit()

    # Refresh the object with the latest database values
    db.refresh(user)

    return user
