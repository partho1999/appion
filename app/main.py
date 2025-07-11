from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.address import router as address_router
from app.api.appointment import router as appointment_router
from app.api.doctor import router as doctor_router
from app.api.dashboard import router as dashboard_router
from app.api.patient import router as patient_router
from app.db.session import AsyncSessionLocal
from app.core.address_loader import load_addresses_if_empty
from app.core.scheduler import start_scheduler
import asyncio

app = FastAPI(title="Appion Appointment Booking System")

@app.on_event("startup")
def startup_event():
    async def load():
        async with AsyncSessionLocal() as db:
            await load_addresses_if_empty(db)
    asyncio.create_task(load())
    start_scheduler()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(address_router)
app.include_router(appointment_router)
app.include_router(doctor_router)
app.include_router(dashboard_router)
app.include_router(patient_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Appion!"} 