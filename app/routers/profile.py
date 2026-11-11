
from fastapi import APIRouter, Depends, File, UploadFile, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.services import profile_service
from app.models.user import User
from app.schemas.profile_response import ProfileResponse
from app.schemas.profile import ProfileUpdate
from app.services.profile_service import (
    upload_profile_picture as upload_profile_picture_service
)


router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.post("/upload-picture")
def upload_profile_picture_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_user = upload_profile_picture_service(
        db=db,
        user_id=current_user.id,
        file=file
    )

    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture": updated_user.profile_picture
    }


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return profile_service.get_my_profile(current_user)


@router.get("/download")
def download_my_profile(
    format: str = Query("pdf", description="Export format: 'pdf' or 'csv'"),
    current_user: User = Depends(get_current_user)
):
    profile_data = profile_service.get_my_profile(current_user)

    if format.lower() == "csv":
        csv_buffer = profile_service.export_profile_csv(current_user, profile_data)
        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=profile_{current_user.id}.csv"
            }
        )

    pdf_buffer = profile_service.export_profile_pdf(current_user, profile_data)
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=profile_{current_user.id}.pdf"
        }
    )






@router.put("/me")
def update_my_profile(payload: ProfileUpdate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    updated_user = profile_service.update_customer_profile(db=db,user_id=current_user.id,payload=payload)

    if updated_user is None:
        return {
            "message": "No profile fields provided or user not found"
        }

    return {
        "message": "Profile updated successfully",
        "profile": profile_service.get_my_profile(updated_user)
    }
