
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric
from sqlalchemy.sql import func

from app.database.connection import Base


class Book(Base):

    __tablename__ = "books"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic book information
    title = Column(String(255), nullable=False)
    author = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    # Book identification
    isbn = Column(String(20), unique=True, index=True, nullable=False)

    # Pricing and inventory
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    # Book category
    category = Column(String(100), nullable=False)

    # Book cover image stored in Storj
    cover_image = Column(String(500), nullable=True)

    # Book availability
    is_active = Column(Boolean, default=True, nullable=False)

    # Creation timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
