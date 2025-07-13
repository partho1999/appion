from pydantic import BaseModel, EmailStr, validator
from pydantic import root_validator  # for v1 compatibility
try:
    from pydantic import model_validator  # v2
except ImportError:
    model_validator = None
from typing import Optional
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
    available_timeslots: Optional[str] = None  # Accept as comma-separated string
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

    if model_validator:
        @model_validator(mode='after')
        def validate_doctor_fields_v2(cls, values):
            if getattr(values, 'role', None) == UserRole.doctor:
                for field in ['license_number', 'experience_years', 'consultation_fee', 'available_timeslots', 'specialization']:
                    val = getattr(values, field, None)
                    if val is None or (isinstance(val, str) and not val.strip()):
                        raise ValueError(f'{field} is required for doctor registration')
            return values
    else:
        @root_validator
        def validate_doctor_fields_v1(cls, values):
            if values.get('role') == UserRole.doctor:
                for field in ['license_number', 'experience_years', 'consultation_fee', 'available_timeslots', 'specialization']:
                    val = values.get(field)
                    if val is None or (isinstance(val, str) and not val.strip()):
                        raise ValueError(f'{field} is required for doctor registration')
            return values

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class DoctorScheduleUpdate(BaseModel):
    available_timeslots: str  # Accept as comma-separated string
    consultation_fee: Optional[float] = None
    specialization: Optional[str] = None

    @validator('available_timeslots')
    def validate_timeslots(cls, v):
        if not v:
            raise ValueError('At least one timeslot must be provided')
        timeslots = [ts.strip() for ts in v.split(',')]
        for timeslot in timeslots:
            if not isinstance(timeslot, str) or '-' not in timeslot:
                raise ValueError('Timeslots must be in format "HH:MM-HH:MM"')
            try:
                start, end = timeslot.split('-')
                datetime.strptime(start.strip(), '%H:%M')
                datetime.strptime(end.strip(), '%H:%M')
            except:
                raise ValueError('Timeslots must be in format "HH:MM-HH:MM"')
        return v 