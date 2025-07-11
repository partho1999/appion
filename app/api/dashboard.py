from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.appointment import Appointment, AppointmentStatus
from app.api._response import envelope_endpoint

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/admin")
@envelope_endpoint
async def admin_dashboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    total_users = (await db.execute(select(User))).scalars().all()
    total_appointments = (await db.execute(select(Appointment))).scalars().all()
    total_doctors = [u for u in total_users if u.role == UserRole.doctor]
    total_patients = [u for u in total_users if u.role == UserRole.patient]
    return {
        "total_users": len(total_users),
        "total_doctors": len(total_doctors),
        "total_patients": len(total_patients),
        "total_appointments": len(total_appointments),
    }

@router.get("/doctor")
@envelope_endpoint
async def doctor_dashboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctors only.")
    appts = (await db.execute(select(Appointment).where(Appointment.doctor_id == current_user.id))).scalars().all()
    completed = [a for a in appts if a.status == AppointmentStatus.completed]
    pending = [a for a in appts if a.status == AppointmentStatus.pending]
    return {
        "total_appointments": len(appts),
        "completed_appointments": len(completed),
        "pending_appointments": len(pending),
    }

@router.get("/patient")
@envelope_endpoint
async def patient_dashboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.patient:
        raise HTTPException(status_code=403, detail="Patients only.")
    appts = (await db.execute(select(Appointment).where(Appointment.patient_id == current_user.id))).scalars().all()
    completed = [a for a in appts if a.status == AppointmentStatus.completed]
    pending = [a for a in appts if a.status == AppointmentStatus.pending]
    return {
        "total_appointments": len(appts),
        "completed_appointments": len(completed),
        "pending_appointments": len(pending),
    } 