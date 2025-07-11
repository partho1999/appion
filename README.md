# Appion: Appointment Booking System

A comprehensive appointment booking system for healthcare providers and patients.

## Tech Stack
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL

## Features
- Patient and doctor profile management
- Appointment scheduling and management
- Doctor schedule management
- Reporting for healthcare providers

---

## Project Structure
```text
appion/
├── README.md
├── requirements.txt
├── alembic.ini
└── app/
    ├── main.py                # FastAPI entrypoint
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   └── config.py          # Settings and environment config
    ├── db/
    │   ├── __init__.py
    │   ├── base.py            # SQLAlchemy base
    │   └── session.py         # Async DB session
    ├── models/
    │   └── __init__.py
    ├── schemas/
    │   └── __init__.py
    ├── crud/
    │   └── __init__.py
    ├── api/
    │   └── __init__.py
    └── alembic/
        ├── env.py             # Alembic migration env
        └── script.py.mako     # Alembic migration template
```

This project is production-ready and follows best practices for structure and maintainability.

---

## API Security & Usage
- All endpoints are protected with JWT authentication.
- Use `/api/v1/auth/register` and `/api/v1/auth/login` to create and authenticate users.
- Only authenticated users can access booking, profile, and dashboard endpoints.
- Role-based access: Admin, Doctor, Patient.
- File uploads (profile images) are validated and stored securely.

## Role-Based Dashboards
- **Admin:** `/api/v1/dashboard/admin` — See/manage all users, appointments, and reports.
- **Doctor:** `/api/v1/dashboard/doctor` — Manage own schedule, appointments, and status.
- **Patient:** `/api/v1/dashboard/patient` — Book appointments, view history, manage profile.

---

## Running the Project
1. Install dependencies: `pip install -r requirements.txt`
2. Run Alembic migrations to set up the database.
3. Start the FastAPI app: `uvicorn app.main:app --reload`

---

## Security Best Practices
- All user input is validated (passwords, emails, files, etc.).
- JWT tokens are used for authentication and authorization.
- Sensitive data is never exposed in API responses.
- Only authorized users can access or modify their own data. 