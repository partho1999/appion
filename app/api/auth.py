from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.services.user import create_user, authenticate_user, get_user_by_email, get_user_by_mobile
from app.db.session import get_db
from app.core.security import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserRole
from app.core.validators import validate_password, validate_mobile, validate_image
import os
import shutil

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '../static/uploads/profile_images')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/register", response_model=UserRead)
async def register(
    full_name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    role: UserRole = Form(...),
    division_id: int = Form(...),
    district_id: int = Form(...),
    thana_id: int = Form(...),
    license_number: str = Form(None),
    experience_years: int = Form(None),
    consultation_fee: float = Form(None),
    available_timeslots: str = Form(None),
    specialization: str = Form(None),
    profile_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    # Validate email/mobile uniqueness
    if await get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if await get_user_by_mobile(db, mobile):
        raise HTTPException(status_code=400, detail="Mobile number already registered.")
    validate_password(password)
    validate_mobile(mobile)
    image_path = None
    if profile_image:
        validate_image(profile_image)
        ext = os.path.splitext(profile_image.filename)[1]
        image_filename = f"{email.replace('@', '_')}{ext}"
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        image_path = os.path.relpath(image_path, os.path.dirname(__file__))
    # Doctor fields
    doctor_fields = {}
    if role == UserRole.doctor:
        if not all([license_number, experience_years, consultation_fee, available_timeslots, specialization]):
            raise HTTPException(status_code=400, detail="All doctor fields are required.")
        doctor_fields = {
            "license_number": license_number,
            "experience_years": experience_years,
            "consultation_fee": consultation_fee,
            "available_timeslots": available_timeslots,
            "specialization": specialization,
        }
    user_in = UserCreate(
        full_name=full_name,
        email=email,
        mobile=mobile,
        password=password,
        role=role,
        division_id=division_id,
        district_id=district_id,
        thana_id=thana_id,
        profile_image=image_path,
        **doctor_fields
    )
    user = await create_user(db, user_in)
    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    # Stateless JWT: client just deletes token
    return {"message": "Successfully logged out."} 