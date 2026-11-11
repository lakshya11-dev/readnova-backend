
import io
import csv
import uuid
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.schemas.profile import ProfileUpdate
from app.repositories.profile_repository import update_profile

from app.repositories.user_repository import (get_user_by_id, update_profile_picture)
from app.services.storage_service import (
    upload_file_to_storj,
    delete_file_from_storj,
    generate_file_url
)


ALLOWED_CONTENT_TYPES = {"image/jpeg","image/png","image/webp"}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def upload_profile_picture( db: Session,user_id: int,file: UploadFile):

    # 1. Check whether the user exists
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Validate image type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG and WEBP images are allowed"
        )

    # 3. Read image data
    file_bytes = file.file.read()

    # 4. Validate image size
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must not exceed 5 MB"
        )

    # 5. Generate a unique object name
    extension = file.filename.rsplit(".", 1)[-1].lower()
    object_name = (
        f"profile_pictures/user_{user_id}/{uuid.uuid4()}.{extension}"
    )

    # 6. Upload image to Storj
    upload_file_to_storj(
        file_bytes=file_bytes,
        object_name=object_name,
        content_type=file.content_type
    )

    # 7. Save object key in PostgreSQL
    old_picture = user.profile_picture

    try:
        updated_user = update_profile_picture(
            db,
            user_id,
            object_name
        )
    except Exception:
        # Remove newly uploaded image if database update fails
        delete_file_from_storj(object_name)
        raise

    # 8. Delete previous picture after successful update
    if old_picture:
        delete_file_from_storj(old_picture)

    return updated_user



def get_my_profile(user):
    profile_picture_url = None

    if user.profile_picture:
        profile_picture_url = generate_file_url(
            user.profile_picture
        )

    from app.services.plan_service import get_user_plan_data
    plan_info = get_user_plan_data(user.id)

    return {
        "id": user.id,
        "name": user.name,
        "full_name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": getattr(user, "is_verified", False) or user.is_active,

        # Customer contact information
        "phone_number": user.phone_number,

        # Delivery address
        "address": user.address,
        "city": user.city,
        "state": user.state,
        "country": user.country,
        "postal_code": user.postal_code,

        # Location coordinates
        "latitude": user.latitude,
        "longitude": user.longitude,

        # Storj profile picture
        "profile_picture_url": profile_picture_url,

        # Pricing plan & subscription
        "plan_name": plan_info.get("plan_name", "Free"),
        "plan_status": plan_info.get("plan_status", "active"),
        "plan_duration_hours": plan_info.get("duration_hours"),
        "plan_activated_at": plan_info.get("activated_at"),
        "plan_expires_at": plan_info.get("expires_at"),
    }






def update_customer_profile(
    db: Session,
    user_id: int,
    payload: ProfileUpdate
):
    # Get only the fields supplied by the customer
    update_data = payload.model_dump(exclude_unset=True)

    # Support full_name by mapping it to the name database column
    if "full_name" in update_data:
        if not update_data.get("name"):
            update_data["name"] = update_data["full_name"]
        del update_data["full_name"]

    # Check that at least one field was provided
    if not update_data:
        return None

    # Update the customer profile through the repository
    updated_user = update_profile(
        db=db,
        user_id=user_id,
        update_data=update_data
    )

    return updated_user


def export_profile_pdf(user, profile_data: dict) -> io.BytesIO:
    """Generate a clean, formatted PDF document containing user profile details."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    elements = []

    # Title & Header
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=20
    )

    elements.append(Paragraph("User Profile Summary", title_style))
    created_ts = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    elements.append(Paragraph(f"Exported on {created_ts}", subtitle_style))

    # Profile Data Table
    table_data = [
        ["Field", "Details"],
        ["User ID", str(profile_data.get("id") or "")],
        ["Full Name", str(profile_data.get("name") or "N/A")],
        ["Email Address", str(profile_data.get("email") or "N/A")],
        ["Role", str(profile_data.get("role") or "N/A").title()],
        ["Account Status", "Active" if profile_data.get("is_active") else "Inactive"],
        ["Email Verified", "Yes" if getattr(user, "is_verified", False) else "No"],
        ["Phone Number", str(profile_data.get("phone_number") or "N/A")],
        ["Street Address", str(profile_data.get("address") or "N/A")],
        ["City", str(profile_data.get("city") or "N/A")],
        ["State / Province", str(profile_data.get("state") or "N/A")],
        ["Country", str(profile_data.get("country") or "N/A")],
        ["Postal Code", str(profile_data.get("postal_code") or "N/A")],
        ["Latitude", str(profile_data.get("latitude") or "N/A")],
        ["Longitude", str(profile_data.get("longitude") or "N/A")],
        ["Profile Picture", "Uploaded (Storj)" if profile_data.get("profile_picture_url") else "Not uploaded"],
    ]

    table = Table(table_data, colWidths=[150, 380])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 1), (0, -1), colors.HexColor("#374151")),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica"),
        ("TEXTCOLOR", (1, 1), (1, -1), colors.HexColor("#1F2937")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def export_profile_csv(user, profile_data: dict) -> io.StringIO:
    """Generate a CSV document containing user profile details."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Field", "Value"])
    writer.writerow(["ID", profile_data.get("id")])
    writer.writerow(["Name", profile_data.get("name")])
    writer.writerow(["Email", profile_data.get("email")])
    writer.writerow(["Role", profile_data.get("role")])
    writer.writerow(["Is Active", profile_data.get("is_active")])
    writer.writerow(["Is Verified", getattr(user, "is_verified", False)])
    writer.writerow(["Phone Number", profile_data.get("phone_number") or ""])
    writer.writerow(["Address", profile_data.get("address") or ""])
    writer.writerow(["City", profile_data.get("city") or ""])
    writer.writerow(["State", profile_data.get("state") or ""])
    writer.writerow(["Country", profile_data.get("country") or ""])
    writer.writerow(["Postal Code", profile_data.get("postal_code") or ""])
    writer.writerow(["Latitude", profile_data.get("latitude") or ""])
    writer.writerow(["Longitude", profile_data.get("longitude") or ""])
    writer.writerow(["Profile Picture URL", profile_data.get("profile_picture_url") or ""])
    buffer.seek(0)
    return buffer
