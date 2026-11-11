
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
    Text,
    CheckConstraint,
    Index
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Order(Base):

    __tablename__ = "orders"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Customer reference
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Order amount
    total_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    # Delivery information snapshot
    delivery_address = Column(
        Text,
        nullable=False
    )

    delivery_phone = Column(
        String(20),
        nullable=True
    )

    # Order status
    order_status = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    # Payment status
    payment_status = Column(
        String(30),
        nullable=False,
        default="pending"
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

    # Relationships
    user = relationship("User")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # Database constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0",
            name="check_order_total_amount"
        ),
        CheckConstraint(
            "order_status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')",
            name="check_order_status"
        ),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'failed', 'refunded')",
            name="check_payment_status"
        ),
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_order_status", "order_status"),
    )


class OrderItem(Base):

    __tablename__ = "order_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Order reference
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    # Book reference
    book_id = Column(
        Integer,
        ForeignKey("books.id", ondelete="RESTRICT"),
        nullable=False
    )

    # Book details snapshot
    book_title = Column(
        String(255),
        nullable=False
    )

    book_author = Column(
        String(150),
        nullable=False
    )

    # Purchase information
    quantity = Column(
        Integer,
        nullable=False
    )

    price_at_purchase = Column(
        Numeric(10, 2),
        nullable=False
    )

    # Relationships
    order = relationship(
        "Order",
        back_populates="items"
    )

    book = relationship("Book")

    @property
    def book_cover_image(self):
        if self.book and getattr(self.book, "cover_image", None):
            return self.book.cover_image
        return None

    # Database constraints
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_order_item_quantity"
        ),
        CheckConstraint(
            "price_at_purchase >= 0",
            name="check_order_item_price"
        ),
    )
