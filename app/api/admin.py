from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy import and_, or_  # type: ignore
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentStatusUpdate
from app.services.appointment import update_appointment_status
from typing import Optional, List
from datetime import datetime, timedelta
from app.api._response import envelope_endpoint

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/appointments")
@envelope_endpoint
async def list_all_appointments(
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
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
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
        query = query.where(
            or_(
                Appointment.notes.ilike(f"%{search}%"),
                Appointment.symptoms.ilike(f"%{search}%")
            )
        )
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/appointments/{appointment_id}/status")
@envelope_endpoint
async def admin_update_appointment_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
    updated = await update_appointment_status(db, appointment_id, status_update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return updated

@router.get("/doctors")
@envelope_endpoint
async def list_all_doctors(
    specialization: Optional[str] = Query(None),
    division_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
    query = select(User).where(User.role == UserRole.doctor)
    if specialization:
        query = query.where(User.specialization == specialization)
    if division_id:
        query = query.where(User.division_id == division_id)
    if district_id:
        query = query.where(User.district_id == district_id)
    if search:
        query = query.where(User.full_name.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/patients")
@envelope_endpoint
async def list_all_patients(
    division_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
    query = select(User).where(User.role == UserRole.patient)
    if division_id:
        query = query.where(User.division_id == division_id)
    if district_id:
        query = query.where(User.district_id == district_id)
    if search:
        query = query.where(User.full_name.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/doctors/{doctor_id}/status")
@envelope_endpoint
async def update_doctor_status(
    doctor_id: int,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
    result = await db.execute(select(User).where(User.id == doctor_id, User.role == UserRole.doctor))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    
    doctor.is_active = is_active
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor

@router.get("/reports/monthly")
@envelope_endpoint
async def generate_monthly_report(
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
    # Calculate date range for the specified month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    # Get all doctors
    doctors_result = await db.execute(select(User).where(User.role == UserRole.doctor))
    doctors = doctors_result.scalars().all()
    
    report_data = []
    total_appointments = 0
    total_earnings = 0
    total_patients = set()
    
    for doctor in doctors:
        # Get appointments for this doctor in the specified month
        appointments_result = await db.execute(
            select(Appointment).where(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_datetime.between(start_date, end_date),
                Appointment.status == AppointmentStatus.completed
            )
        )
        appointments = appointments_result.scalars().all()
        
        doctor_appointments = len(appointments)
        doctor_earnings = sum([doctor.consultation_fee or 0 for _ in appointments])
        doctor_patients = len(set([appt.patient_id for appt in appointments]))
        
        total_appointments += doctor_appointments
        total_earnings += doctor_earnings
        total_patients.update([appt.patient_id for appt in appointments])
        
        report_data.append({
            "doctor_id": doctor.id,
            "doctor_name": doctor.full_name,
            "specialization": doctor.specialization,
            "total_appointments": doctor_appointments,
            "total_earnings": doctor_earnings,
            "total_patients": doctor_patients,
            "consultation_fee": doctor.consultation_fee
        })
    
    return {
        "period": f"{year}-{month:02d}",
        "total_doctors": len(doctors),
        "total_appointments": total_appointments,
        "total_earnings": total_earnings,
        "total_unique_patients": len(total_patients),
        "doctor_reports": report_data
    }

@router.get("/reports/doctor/{doctor_id}")
@envelope_endpoint
async def generate_doctor_report(
    doctor_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    
    # Get doctor
    doctor_result = await db.execute(select(User).where(User.id == doctor_id, User.role == UserRole.doctor))
    doctor = doctor_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    
    # Build query
    query = select(Appointment).where(Appointment.doctor_id == doctor_id)
    if start_date:
        query = query.where(Appointment.appointment_datetime >= start_date)
    if end_date:
        query = query.where(Appointment.appointment_datetime <= end_date)
    
    appointments_result = await db.execute(query)
    appointments = appointments_result.scalars().all()
    
    # Calculate statistics
    total_appointments = len(appointments)
    completed_appointments = len([a for a in appointments if a.status == AppointmentStatus.completed])
    pending_appointments = len([a for a in appointments if a.status == AppointmentStatus.pending])
    cancelled_appointments = len([a for a in appointments if a.status == AppointmentStatus.cancelled])
    total_earnings = sum([doctor.consultation_fee or 0 for a in appointments if a.status == AppointmentStatus.completed])
    unique_patients = len(set([a.patient_id for a in appointments]))
    
    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.full_name,
        "specialization": doctor.specialization,
        "consultation_fee": doctor.consultation_fee,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "pending_appointments": pending_appointments,
        "cancelled_appointments": cancelled_appointments,
        "total_earnings": total_earnings,
        "unique_patients": unique_patients,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    } 