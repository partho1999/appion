from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus

class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_datetime: datetime
    notes: Optional[str] = None
    symptoms: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentRead(AppointmentBase):
    id: int
    patient_id: int
    status: AppointmentStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus 