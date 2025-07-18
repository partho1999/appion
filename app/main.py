from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.address import router as address_router
from app.api.appointment import router as appointment_router
from app.api.doctor import router as doctor_router
from app.api.dashboard import router as dashboard_router
from app.api.patient import router as patient_router
from app.api.admin import router as admin_router
from app.db.session import AsyncSessionLocal
from app.core.address_loader import load_addresses_if_empty
from app.core.scheduler import start_scheduler
import asyncio

app = FastAPI(title="Appion Appointment Booking System")

# Mount static directory for profile images
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Appion API!",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "user": "/api/v1/user", 
            "address": "/api/address",
            "appointment": "/api/v1/appointments",
            "doctor": "/api/v1/doctors",
            "dashboard": "/api/v1/dashboard",
            "patient": "/api/v1/patients",
            "admin": "/api/v1/admin"
        },
        "docs": "/docs"
    } 