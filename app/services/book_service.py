from sqlalchemy.orm import Session

from app.repositories.book_repository import (
    create_book,
    get_all_books,
    get_book_by_id,
    get_book_by_isbn,
    update_book,
    delete_book
)
from app.services.storage_service import (
    upload_file_to_storj,
    delete_file_from_storj
)


class BookAlreadyExistsError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


def add_book(db: Session, book_data):
    isbn = book_data.isbn.strip() if (book_data.isbn and isinstance(book_data.isbn, str) and book_data.isbn.strip()) else None

    if not isbn:
        import random
        while True:
            generated = f"978{random.randint(1000000000, 9999999999)}"
            if not get_book_by_isbn(db, generated):
                isbn = generated
                break
    else:
        existing_book = get_book_by_isbn(
            db,
            isbn
        )

        if existing_book:
            raise BookAlreadyExistsError(
                "A book with this ISBN already exists"
            )

    data_dict = book_data.model_dump()
    data_dict["isbn"] = isbn
    if data_dict.get("category") and isinstance(data_dict["category"], str) and data_dict["category"].strip():
        data_dict["category"] = data_dict["category"].strip().capitalize()
    else:
        data_dict["category"] = "General"

    # Make sure only valid model columns are passed to Book
    valid_keys = {"title", "author", "description", "isbn", "price", "stock", "category", "cover_image", "is_active"}
    clean_data = {k: v for k, v in data_dict.items() if k in valid_keys}

    return create_book(db, clean_data)


def get_books(db: Session):
    return get_all_books(db)


def get_book(db: Session, book_id: int):
    book = get_book_by_id(db, book_id)

    if not book:
        raise BookNotFoundError("Book not found")

    return book


def edit_book(db: Session, book_id: int, book_data):
    book = get_book_by_id(db, book_id)

    if not book:
        raise BookNotFoundError("Book not found")

    update_data = book_data.model_dump(exclude_unset=True)

    valid_keys = {"title", "author", "description", "isbn", "price", "stock", "category", "cover_image", "is_active"}
    clean_data = {k: v for k, v in update_data.items() if k in valid_keys}

    if "category" in clean_data and isinstance(clean_data["category"], str) and clean_data["category"].strip():
        clean_data["category"] = clean_data["category"].strip().capitalize()

    return update_book(db, book, clean_data)


def remove_book(db: Session, book_id: int):
    book = get_book_by_id(db, book_id)

    if not book:
        raise BookNotFoundError("Book not found")

    delete_book(db, book)

    return {"message": "Book deleted successfully"}


def upload_book_cover(
    db: Session,
    book_id: int,
    file_bytes: bytes,
    object_name: str,
    content_type: str
):
    # Find the book
    book = get_book_by_id(db, book_id)

    if not book:
        raise BookNotFoundError("Book not found")

    # Upload the new cover to Storj
    upload_file_to_storj(
        file_bytes,
        object_name,
        content_type
    )

    # Remember the previous cover
    old_cover = book.cover_image

    # Save the new Storj object name in PostgreSQL
    update_book(
        db,
        book,
        {"cover_image": object_name}
    )

    # Delete the previous cover, if one existed
    if old_cover:
        delete_file_from_storj(old_cover)

    return book
