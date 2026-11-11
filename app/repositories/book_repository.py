
from sqlalchemy.orm import Session

from app.models.book import Book


def create_book(db: Session, book_data: dict):

    new_book = Book(**book_data)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book



def get_book_by_id(db: Session, book_id: int):

    return db.query(Book).filter(
        Book.id == book_id
    ).first()


def update_book(db: Session, book: Book, update_data: dict):

    for key, value in update_data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)

    return book


def delete_book(db: Session, book: Book):

    db.delete(book)
    db.commit()

    return True

def get_book_by_isbn(db: Session, isbn: str):

    return db.query(Book).filter(
        Book.isbn == isbn
    ).first()


def get_all_books(
    db: Session,
    search: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Book).filter(Book.is_active == True)

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            (Book.title.ilike(search_term)) |
            (Book.author.ilike(search_term)) |
            (Book.isbn.ilike(search_term))
        )

    if category:
        query = query.filter(Book.category.ilike(category))

    if min_price is not None:
        query = query.filter(Book.price >= min_price)

    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    return query.offset(skip).limit(limit).all()