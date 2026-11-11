from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from uuid import uuid4
from app.services.book_service import upload_book_cover
from app.database.connection import get_db
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.core.dependencies import require_role
from app.services.book_service import (
    add_book,
    get_all_books,
    get_book,
    edit_book,
    remove_book,
    BookAlreadyExistsError,
    BookNotFoundError
)

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    try:
        return add_book(db, book_data)

    except BookAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )



@router.get("/", response_model=list[BookResponse])
def list_books(
    search: str = Query(default=None),
    category: str = Query(default=None),
    min_price: float = Query(default=None, ge=0),
    max_price: float = Query(default=None, ge=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum price cannot be greater than maximum price"
            )

    return get_all_books(
        db=db,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit
    )



@router.get("/{book_id}", response_model=BookResponse)
def retrieve_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    try:
        return get_book(db, book_id)

    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.put("/{book_id}", response_model=BookResponse)
def update_existing_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    try:
        return edit_book(db, book_id, book_data)

    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.delete("/{book_id}")
def delete_existing_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    try:
        return remove_book(db, book_id)

    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )




@router.post("/{book_id}/cover", response_model=BookResponse)
def upload_book_cover_image(
    book_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    # Allow only image files
    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG and WEBP images are allowed"
        )

    # Read uploaded image
    file_bytes = file.file.read()

    # Generate a unique Storj object name
    extension = file.filename.split(".")[-1].lower()

    object_name = f"book_covers/{uuid4()}.{extension}"

    try:
        return upload_book_cover(
            db,
            book_id,
            file_bytes,
            object_name,
            file.content_type
        )

    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )