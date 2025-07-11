from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from datetime import datetime, timedelta
import logging

scheduler = AsyncIOScheduler()

async def send_appointment_reminders():
    async with AsyncSessionLocal() as db:
        now = datetime.now()
        reminder_time = now + timedelta(days=1)
        result = await db.execute(
            select(Appointment).where(
                Appointment.appointment_datetime.between(reminder_time.replace(hour=0, minute=0, second=0, microsecond=0),
                                                        reminder_time.replace(hour=23, minute=59, second=59, microsecond=999999)),
                Appointment.status == AppointmentStatus.confirmed
            )
        )
        appointments = result.scalars().all()
        for appt in appointments:
            # Here you would send an email/SMS reminder
            logging.info(f"Reminder: Appointment for patient {appt.patient_id} with doctor {appt.doctor_id} at {appt.appointment_datetime}")

async def generate_monthly_report():
    async with AsyncSessionLocal() as db:
        now = datetime.now()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = first_day - timedelta(days=1)
        start = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = last_month.replace(hour=23, minute=59, second=59, microsecond=999999)
        result = await db.execute(
            select(User).where(User.role == UserRole.doctor)
        )
        doctors = result.scalars().all()
        for doctor in doctors:
            appt_result = await db.execute(
                select(Appointment).where(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_datetime.between(start, end),
                    Appointment.status == AppointmentStatus.completed
                )
            )
            appointments = appt_result.scalars().all()
            total_appointments = len(appointments)
            total_earnings = sum([doctor.consultation_fee or 0 for _ in appointments])
            total_patients = len(set([appt.patient_id for appt in appointments]))
            # Here you would generate and send/store the report
            logging.info(f"Monthly Report for Dr.{doctor.full_name}: Visits={total_patients}, Appointments={total_appointments}, Earnings={total_earnings}")

def start_scheduler():
    scheduler.add_job(send_appointment_reminders, 'cron', hour=8, minute=0)
    scheduler.add_job(generate_monthly_report, 'cron', day=1, hour=2, minute=0)
    scheduler.start() 