from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy import and_  # type: ignore
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json

async def get_doctor_schedule(db: AsyncSession, doctor_id: int) -> Optional[Dict[str, Any]]:
    """Get doctor's schedule and availability"""
    result = await db.execute(select(User).where(User.id == doctor_id, User.role == UserRole.doctor))
    doctor = result.scalar_one_or_none()
    if doctor is None:
        return None
    # Parse available timeslots
    timeslots = []
    if doctor.available_timeslots is not None:
        timeslots = [ts.strip() for ts in doctor.available_timeslots.split(',') if ts.strip()]
    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.full_name,
        "specialization": doctor.specialization,
        "available_timeslots": timeslots,
        "consultation_fee": doctor.consultation_fee,
        "experience_years": doctor.experience_years
    }

async def update_doctor_schedule(
    db: AsyncSession, 
    doctor_id: int, 
    available_timeslots: str,
    consultation_fee: Optional[float] = None,
    specialization: Optional[str] = None
) -> Optional[User]:
    """Update doctor's schedule and professional details"""
    result = await db.execute(select(User).where(User.id == doctor_id, User.role == UserRole.doctor))
    doctor = result.scalar_one_or_none()
    if doctor is None:
        return None
    # Update timeslots (store as string)
    doctor.available_timeslots = available_timeslots
    if consultation_fee is not None:
        doctor.consultation_fee = consultation_fee
    if specialization is not None:
        doctor.specialization = specialization
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor

async def is_doctor_available_at_time(
    db: AsyncSession, 
    doctor_id: int, 
    appointment_datetime: datetime
) -> bool:
    """Check if doctor is available at specific time considering their schedule"""
    doctor_result = await db.execute(select(User).where(User.id == doctor_id, User.role == UserRole.doctor))
    doctor = doctor_result.scalar_one_or_none()
    if doctor is None or not getattr(doctor, 'is_active', True):
        return False
    # Check if doctor has defined timeslots
    if doctor.available_timeslots is None:
        return True  # If no schedule defined, assume available
    # Parse timeslots
    timeslots = [ts.strip() for ts in doctor.available_timeslots.split(',') if ts.strip()]
    appointment_time = appointment_datetime.time()
    for timeslot in timeslots:
        if '-' in timeslot:
            try:
                start_str, end_str = timeslot.split('-')
                start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                if start_time <= appointment_time <= end_time:
                    # Check for conflicting appointments
                    return await is_doctor_available_for_appointment(db, doctor_id, appointment_datetime)
            except Exception:
                continue
    return False

async def is_doctor_available_for_appointment(
    db: AsyncSession, 
    doctor_id: int, 
    appointment_datetime: datetime
) -> bool:
    window_start = appointment_datetime - timedelta(minutes=59)
    window_end = appointment_datetime + timedelta(minutes=59)
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_datetime >= window_start,
                Appointment.appointment_datetime <= window_end,
                Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.confirmed])
            )
        )
    )
    return result.scalar_one_or_none() is None

async def get_doctor_appointments(
    db: AsyncSession, 
    doctor_id: int, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[AppointmentStatus] = None
) -> List[Appointment]:
    query = select(Appointment).where(Appointment.doctor_id == doctor_id)
    if start_date is not None:
        query = query.where(Appointment.appointment_datetime >= start_date)
    if end_date is not None:
        query = query.where(Appointment.appointment_datetime <= end_date)
    if status is not None:
        query = query.where(Appointment.status == status)
    result = await db.execute(query)
    return list(result.scalars().all())

async def get_doctor_statistics(
    db: AsyncSession, 
    doctor_id: int, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    appointments = await get_doctor_appointments(db, doctor_id, start_date, end_date)
    total_appointments = len(appointments)
    completed_appointments = len([a for a in appointments if a.status == AppointmentStatus.completed])
    pending_appointments = len([a for a in appointments if a.status == AppointmentStatus.pending])
    cancelled_appointments = len([a for a in appointments if a.status == AppointmentStatus.cancelled])
    doctor_result = await db.execute(select(User).where(User.id == doctor_id))
    doctor = doctor_result.scalar_one_or_none()
    consultation_fee = doctor.consultation_fee if doctor else 0
    total_earnings = completed_appointments * consultation_fee
    unique_patients = len(set([a.patient_id for a in appointments]))
    return {
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "pending_appointments": pending_appointments,
        "cancelled_appointments": cancelled_appointments,
        "total_earnings": total_earnings,
        "unique_patients": unique_patients,
        "consultation_fee": consultation_fee
    } 