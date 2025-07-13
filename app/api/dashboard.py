from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy import func  # type: ignore
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus
from app.api._response import envelope_endpoint
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/admin")
@envelope_endpoint
async def admin_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
    # Base queries
    users_query = select(User)
    appointments_query = select(Appointment)
    
    # Apply date filters if provided
    if start_date:
        appointments_query = appointments_query.where(Appointment.appointment_datetime >= start_date)
    if end_date:
        appointments_query = appointments_query.where(Appointment.appointment_datetime <= end_date)
    
    # Get counts
    total_users = (await db.execute(users_query)).scalars().all()
    total_appointments = (await db.execute(appointments_query)).scalars().all()
    
    # Filter by role
    total_doctors = [u for u in total_users if u.role == UserRole.doctor and u.is_active]
    total_patients = [u for u in total_users if u.role == UserRole.patient]
    
    # Appointment statistics
    completed_appointments = [a for a in total_appointments if a.status == AppointmentStatus.completed]
    pending_appointments = [a for a in total_appointments if a.status == AppointmentStatus.pending]
    cancelled_appointments = [a for a in total_appointments if a.status == AppointmentStatus.cancelled]
    
    # Calculate total earnings
    total_earnings = 0
    for appt in completed_appointments:
        doctor_result = await db.execute(select(User).where(User.id == appt.doctor_id))
        doctor = doctor_result.scalar_one_or_none()
        if doctor and doctor.consultation_fee:
            total_earnings += doctor.consultation_fee
    
    return {
        "total_users": len(total_users),
        "total_doctors": len(total_doctors),
        "total_patients": len(total_patients),
        "total_appointments": len(total_appointments),
        "completed_appointments": len(completed_appointments),
        "pending_appointments": len(pending_appointments),
        "cancelled_appointments": len(cancelled_appointments),
        "total_earnings": total_earnings,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

@router.get("/doctor")
@envelope_endpoint
async def doctor_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctors only.")
    
    # Build query for doctor's appointments
    query = select(Appointment).where(Appointment.doctor_id == current_user.id)
    
    if start_date:
        query = query.where(Appointment.appointment_datetime >= start_date)
    if end_date:
        query = query.where(Appointment.appointment_datetime <= end_date)
    
    appointments = (await db.execute(query)).scalars().all()
    
    # Calculate statistics
    completed = [a for a in appointments if a.status == AppointmentStatus.completed]
    pending = [a for a in appointments if a.status == AppointmentStatus.pending]
    confirmed = [a for a in appointments if a.status == AppointmentStatus.confirmed]
    cancelled = [a for a in appointments if a.status == AppointmentStatus.cancelled]
    
    # Calculate earnings
    total_earnings = len(completed) * (current_user.consultation_fee or 0)
    
    # Get unique patients
    unique_patients = len(set([a.patient_id for a in appointments]))
    
    return {
        "total_appointments": len(appointments),
        "completed_appointments": len(completed),
        "pending_appointments": len(pending),
        "confirmed_appointments": len(confirmed),
        "cancelled_appointments": len(cancelled),
        "total_earnings": total_earnings,
        "unique_patients": unique_patients,
        "consultation_fee": current_user.consultation_fee,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

@router.get("/patient")
@envelope_endpoint
async def patient_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.patient:
        raise HTTPException(status_code=403, detail="Patients only.")
    
    # Build query for patient's appointments
    query = select(Appointment).where(Appointment.patient_id == current_user.id)
    
    if start_date:
        query = query.where(Appointment.appointment_datetime >= start_date)
    if end_date:
        query = query.where(Appointment.appointment_datetime <= end_date)
    
    appointments = (await db.execute(query)).scalars().all()
    
    # Calculate statistics
    completed = [a for a in appointments if a.status == AppointmentStatus.completed]
    pending = [a for a in appointments if a.status == AppointmentStatus.pending]
    confirmed = [a for a in appointments if a.status == AppointmentStatus.confirmed]
    cancelled = [a for a in appointments if a.status == AppointmentStatus.cancelled]
    
    # Get unique doctors
    unique_doctors = len(set([a.doctor_id for a in appointments]))
    
    return {
        "total_appointments": len(appointments),
        "completed_appointments": len(completed),
        "pending_appointments": len(pending),
        "confirmed_appointments": len(confirmed),
        "cancelled_appointments": len(cancelled),
        "unique_doctors": unique_doctors,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    } 