from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    mobile: str
    division_id: Optional[int]
    district_id: Optional[int]
    thana_id: Optional[int]
    profile_image: Optional[str] = None
    # Doctor-specific fields
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    available_timeslots: Optional[List[str]] = None
    specialization: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @validator('mobile')
    def validate_mobile(cls, v):
        if not v.startswith('+88') or len(v) != 14 or not v[1:].isdigit():
            raise ValueError('Mobile number must start with +88 and be exactly 14 digits')
        return v

    @validator('password')
    def validate_password(cls, v):
        import re
        if (len(v) < 8 or not re.search(r'[A-Z]', v) or not re.search(r'\d', v) or not re.search(r'[^A-Za-z0-9]', v)):
            raise ValueError('Password must be at least 8 characters, include 1 uppercase, 1 digit, 1 special character')
        return v

    @validator('role')
    def validate_doctor_fields(cls, v, values):
        if v == UserRole.doctor:
            for field in ['license_number', 'experience_years', 'consultation_fee', 'available_timeslots']:
                if not values.get(field):
                    raise ValueError(f'{field} is required for doctor registration')
        return v

class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str 