from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy import and_  # type: ignore
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate
from datetime import datetime, timedelta

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
    # Check if doctor has an appointment at the same time (±1 hour window)
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
    return result.scalars().first() is None

async def update_appointment_status(db: AsyncSession, appointment_id: int, status: AppointmentStatus):
    appointment = await get_appointment_by_id(db, appointment_id)
    if appointment:
        appointment.status = status
        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)
    return appointment 