from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentStatusUpdate
from app.services.appointment import create_appointment, get_appointments_for_user, is_doctor_available, update_appointment_status, get_appointment_by_id
from app.models.user import User, UserRole
from app.models.appointment import AppointmentStatus
from datetime import datetime, time
from typing import Optional
from app.api._response import envelope_endpoint

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])

BUSINESS_HOURS_START = time(8, 0)
BUSINESS_HOURS_END = time(18, 0)

@router.post("/", response_model=AppointmentRead)
@envelope_endpoint
async def book_appointment(
    appointment_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only patients can book
    if current_user.role != UserRole.patient:
        raise HTTPException(status_code=403, detail="Only patients can book appointments.")
    # Validate not in the past
    if appointment_in.appointment_datetime < datetime.now():
        raise HTTPException(status_code=400, detail="Appointment cannot be in the past.")
    # Validate business hours
    appt_time = appointment_in.appointment_datetime.time()
    if not (BUSINESS_HOURS_START <= appt_time <= BUSINESS_HOURS_END):
        raise HTTPException(status_code=400, detail="Appointment must be within business hours (08:00-18:00).")
    # Validate doctor availability
    available = await is_doctor_available(db, appointment_in.doctor_id, appointment_in.appointment_datetime)
    if not available:
        raise HTTPException(status_code=400, detail="Doctor is not available at this time.")
    appointment = await create_appointment(db, current_user.id, appointment_in)
    return appointment

@router.get("/", response_model=list[AppointmentRead])
@envelope_endpoint
async def list_appointments(
    status: Optional[AppointmentStatus] = None,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy.future import select
    from sqlalchemy import and_, or_
    query = select(Appointment).where(
        or_(Appointment.patient_id == current_user.id, Appointment.doctor_id == current_user.id)
    )
    if status:
        query = query.where(Appointment.status == status)
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.where(Appointment.patient_id == patient_id)
    if start_date:
        query = query.where(Appointment.appointment_datetime >= start_date)
    if end_date:
        query = query.where(Appointment.appointment_datetime <= end_date)
    if search:
        query = query.where((Appointment.notes.ilike(f"%{search}%")) | (Appointment.symptoms.ilike(f"%{search}%")))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
@envelope_endpoint
async def update_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only doctors can update status
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Only doctors can update appointment status.")
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment or appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    updated = await update_appointment_status(db, appointment_id, status_update.status)
    return updated 