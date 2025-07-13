from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentStatusUpdate
from app.services.appointment import (
    create_appointment, 
    get_appointments_with_filters, 
    is_doctor_available, 
    update_appointment_status, 
    get_appointment_by_id,
    cancel_appointment,
    get_appointment_statistics
)
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
    
    # Validate doctor availability (enhanced check)
    available = await is_doctor_available(db, appointment_in.doctor_id, appointment_in.appointment_datetime)
    if not available:
        raise HTTPException(status_code=400, detail="Doctor is not available at this time.")
    
    appointment = await create_appointment(db, current_user.id, appointment_in)
    return appointment

@router.get("/", response_model=dict)
@envelope_endpoint
async def list_appointments(
    status: Optional[AppointmentStatus] = Query(None),
    doctor_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get appointments with enhanced filtering and pagination"""
    result = await get_appointments_with_filters(
        db=db,
        user_id=current_user.id,
        role=current_user.role.value,
        status=status,
        doctor_id=doctor_id,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        skip=skip,
        limit=limit
    )
    return result

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

@router.delete("/{appointment_id}")
@envelope_endpoint
async def cancel_appointment_endpoint(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an appointment"""
    cancelled = await cancel_appointment(db, appointment_id, current_user.id, current_user.role.value)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Appointment not found or cannot be cancelled.")
    return {"message": "Appointment cancelled successfully"}

@router.get("/statistics")
@envelope_endpoint
async def get_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get appointment statistics for the current user"""
    stats = await get_appointment_statistics(
        db, 
        current_user.id, 
        current_user.role.value, 
        start_date, 
        end_date
    )
    return stats

@router.get("/{appointment_id}", response_model=AppointmentRead)
@envelope_endpoint
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific appointment details"""
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    
    # Check authorization
    if current_user.role == UserRole.patient and appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this appointment.")
    elif current_user.role == UserRole.doctor and appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this appointment.")
    # Admin can view any appointment
    
    return appointment 