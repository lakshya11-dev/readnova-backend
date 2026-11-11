
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    CheckConstraint
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Cart(Base):

    __tablename__ = "carts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # One cart per customer
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship with User
    user = relationship("User", back_populates="cart")

    # One cart can contain multiple items
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )


class CartItem(Base):

    __tablename__ = "cart_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Cart reference
    cart_id = Column(
        Integer,
        ForeignKey("carts.id"),
        nullable=False
    )

    # Book reference
    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=False
    )

    # Book quantity
    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )

    # Creation timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    cart = relationship("Cart", back_populates="items")
    book = relationship("Book")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "book_id",
            name="unique_book_per_cart"
        ),
        CheckConstraint(
            "quantity > 0",
            name="check_cart_item_quantity"
        ),
    )
