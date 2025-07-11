from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from app.api.deps import get_current_user
from app.schemas.user import UserRead
from app.models.user import User, UserRole
from app.db.session import get_db
from app.core.validators import validate_mobile, validate_image
import os
import shutil
from app.api._response import envelope_endpoint

router = APIRouter(prefix="/api/v1/user", tags=["user"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '../static/uploads/profile_images')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/profile", response_model=UserRead)
@envelope_endpoint
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserRead)
@envelope_endpoint
async def update_profile(
    full_name: str = Form(None),
    mobile: str = Form(None),
    division_id: int = Form(None),
    district_id: int = Form(None),
    thana_id: int = Form(None),
    license_number: str = Form(None),
    experience_years: int = Form(None),
    consultation_fee: float = Form(None),
    available_timeslots: str = Form(None),
    specialization: str = Form(None),
    profile_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = False
    if full_name is not None:
        current_user.full_name = full_name
        updated = True
    if mobile is not None:
        validate_mobile(mobile)
        current_user.mobile = mobile
        updated = True
    if division_id is not None:
        current_user.division_id = division_id
        updated = True
    if district_id is not None:
        current_user.district_id = district_id
        updated = True
    if thana_id is not None:
        current_user.thana_id = thana_id
        updated = True
    if current_user.role == UserRole.doctor:
        if license_number is not None:
            current_user.license_number = license_number
            updated = True
        if experience_years is not None:
            current_user.experience_years = experience_years
            updated = True
        if consultation_fee is not None:
            current_user.consultation_fee = consultation_fee
            updated = True
        if available_timeslots is not None:
            current_user.available_timeslots = available_timeslots
            updated = True
        if specialization is not None:
            current_user.specialization = specialization
            updated = True
    if profile_image is not None:
        validate_image(profile_image)
        ext = os.path.splitext(profile_image.filename)[1]
        image_filename = f"{current_user.email.replace('@', '_')}{ext}"
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        current_user.profile_image = os.path.relpath(image_path, os.path.dirname(__file__))
        updated = True
    if updated:
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
    return current_user 