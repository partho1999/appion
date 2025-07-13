from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy import and_  # type: ignore
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from app.schemas.appointment import AppointmentCreate
from datetime import datetime, timedelta
from app.services.doctor import is_doctor_available_at_time

async def create_appointment(db: AsyncSession, patient_id: int, appointment_in: AppointmentCreate):
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=appointment_in.doctor_id,
        appointment_datetime=appointment_in.appointment_datetime,
        notes=appointment_in.notes,
        symptoms=appointment_in.symptoms,
        status=AppointmentStatus.pending
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment

async def get_appointment_by_id(db: AsyncSession, appointment_id: int):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalars().first()

async def get_appointments_for_user(db: AsyncSession, user_id: int, role: str):
    if role == 'doctor':
        result = await db.execute(select(Appointment).where(Appointment.doctor_id == user_id))
    else:
        result = await db.execute(select(Appointment).where(Appointment.patient_id == user_id))
    return result.scalars().all()

async def is_doctor_available(db: AsyncSession, doctor_id: int, appointment_datetime: datetime) -> bool:
    """Enhanced availability check that considers doctor's schedule"""
    # First check if doctor exists and is active
    doctor_result = await db.execute(select(User).where(User.id == doctor_id, User.role == UserRole.doctor))
    doctor = doctor_result.scalar_one_or_none()
    if not doctor or not doctor.is_active:
        return False
    
    # Use the enhanced availability check from doctor service
    return await is_doctor_available_at_time(db, doctor_id, appointment_datetime)

async def update_appointment_status(db: AsyncSession, appointment_id: int, status: AppointmentStatus):
    appointment = await get_appointment_by_id(db, appointment_id)
    if appointment:
        appointment.status = status
        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)
    return appointment

async def get_appointments_with_filters(
    db: AsyncSession,
    user_id: int,
    role: str,
    status: AppointmentStatus = None,
    doctor_id: int = None,
    patient_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    search: str = None,
    skip: int = 0,
    limit: int = 10
):
    """Get appointments with comprehensive filtering"""
    if role == 'doctor':
        query = select(Appointment).where(Appointment.doctor_id == user_id)
    elif role == 'patient':
        query = select(Appointment).where(Appointment.patient_id == user_id)
    else:  # admin
        query = select(Appointment)
    
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
        from sqlalchemy import or_
        query = query.where(
            or_(
                Appointment.notes.ilike(f"%{search}%"),
                Appointment.symptoms.ilike(f"%{search}%")
            )
        )
    
    # Get total count before pagination
    count_result = await db.execute(query)
    total_count = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return {
        "appointments": appointments,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

async def cancel_appointment(db: AsyncSession, appointment_id: int, user_id: int, role: str):
    """Cancel an appointment with proper authorization"""
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        return None
    
    # Check authorization
    if role == 'patient' and appointment.patient_id != user_id:
        return None
    elif role == 'doctor' and appointment.doctor_id != user_id:
        return None
    # Admin can cancel any appointment
    
    # Only allow cancellation of pending or confirmed appointments
    if appointment.status not in [AppointmentStatus.pending, AppointmentStatus.confirmed]:
        return None
    
    appointment.status = AppointmentStatus.cancelled
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment

async def get_appointment_statistics(
    db: AsyncSession,
    user_id: int,
    role: str,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Get appointment statistics for a user"""
    if role == 'doctor':
        query = select(Appointment).where(Appointment.doctor_id == user_id)
    elif role == 'patient':
        query = select(Appointment).where(Appointment.patient_id == user_id)
    else:  # admin
        query = select(Appointment)
    
    if start_date:
        query = query.where(Appointment.appointment_datetime >= start_date)
    if end_date:
        query = query.where(Appointment.appointment_datetime <= end_date)
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    total = len(appointments)
    pending = len([a for a in appointments if a.status == AppointmentStatus.pending])
    confirmed = len([a for a in appointments if a.status == AppointmentStatus.confirmed])
    completed = len([a for a in appointments if a.status == AppointmentStatus.completed])
    cancelled = len([a for a in appointments if a.status == AppointmentStatus.cancelled])
    
    return {
        "total": total,
        "pending": pending,
        "confirmed": confirmed,
        "completed": completed,
        "cancelled": cancelled
    } 