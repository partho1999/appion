from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.doctor import (
    get_doctor_schedule, 
    update_doctor_schedule, 
    is_doctor_available_at_time,
    get_doctor_appointments,
    get_doctor_statistics
)
from app.api.deps import get_current_user
from app.schemas.user import DoctorScheduleUpdate
from typing import Optional, List
from datetime import datetime
from app.api._response import envelope_endpoint

router = APIRouter(prefix="/api/v1/doctors", tags=["doctors"])

@router.get("/")
@envelope_endpoint
async def list_doctors(
    specialization: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
    division_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    thana_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.role == UserRole.doctor, User.is_active == True)
    if specialization:
        query = query.where(User.specialization == specialization)
    if division_id:
        query = query.where(User.division_id == division_id)
    if district_id:
        query = query.where(User.district_id == district_id)
    if thana_id:
        query = query.where(User.thana_id == thana_id)
    if search:
        query = query.where(User.full_name.ilike(f"%{search}%"))
    if available is not None:
        if available:
            query = query.where(User.available_timeslots.isnot(None))
        else:
            query = query.where(User.available_timeslots.is_(None))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{doctor_id}/schedule")
@envelope_endpoint
async def get_schedule(
    doctor_id: int,
    db: AsyncSession = Depends(get_db)
):
    schedule = await get_doctor_schedule(db, doctor_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    return schedule

@router.put("/schedule")
@envelope_endpoint
async def update_schedule(
    schedule_update: DoctorScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctors only.")
    updated_doctor = await update_doctor_schedule(
        db, 
        current_user.id, 
        schedule_update.available_timeslots, 
        schedule_update.consultation_fee, 
        schedule_update.specialization
    )
    if not updated_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    return updated_doctor

@router.get("/{doctor_id}/availability")
@envelope_endpoint
async def check_availability(
    doctor_id: int,
    appointment_datetime: datetime,
    db: AsyncSession = Depends(get_db)
):
    is_available = await is_doctor_available_at_time(db, doctor_id, appointment_datetime)
    return {
        "doctor_id": doctor_id,
        "appointment_datetime": appointment_datetime,
        "is_available": is_available
    }

@router.get("/appointments")
@envelope_endpoint
async def get_my_appointments(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctors only.")
    from app.models.appointment import AppointmentStatus
    status_enum = None
    if status:
        try:
            status_enum = AppointmentStatus(status)
        except:
            raise HTTPException(status_code=400, detail="Invalid status.")
    appointments = await get_doctor_appointments(
        db, 
        current_user.id, 
        start_date, 
        end_date, 
        status_enum
    )
    total = len(appointments)
    appointments = appointments[skip:skip + limit]
    return {
        "appointments": appointments,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/statistics")
@envelope_endpoint
async def get_my_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctors only.")
    stats = await get_doctor_statistics(db, current_user.id, start_date, end_date)
    return stats

@router.get("/{doctor_id}/appointments")
@envelope_endpoint
async def get_doctor_appointments_admin(
    doctor_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    from app.models.appointment import AppointmentStatus
    status_enum = None
    if status:
        try:
            status_enum = AppointmentStatus(status)
        except:
            raise HTTPException(status_code=400, detail="Invalid status.")
    appointments = await get_doctor_appointments(
        db, 
        doctor_id, 
        start_date, 
        end_date, 
        status_enum
    )
    total = len(appointments)
    appointments = appointments[skip:skip + limit]
    return {
        "appointments": appointments,
        "total": total,
        "skip": skip,
        "limit": limit
    } 