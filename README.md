# Appion: Healthcare Appointment Booking System

A comprehensive, production-ready appointment booking system designed for healthcare providers, patients, and administrators. Built with FastAPI and PostgreSQL, featuring role-based access control, real-time scheduling, and comprehensive reporting capabilities.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Challenges & Assumptions](#challenges--assumptions)

## 🏥 Project Overview

Appion is a modern healthcare appointment booking system that streamlines the process of scheduling medical appointments. The system supports three distinct user roles:

- **Patients**: Can book appointments, view their medical history, and manage their profiles
- **Doctors**: Can manage their schedules, view patient appointments, and update appointment statuses
- **Administrators**: Can oversee all operations, generate reports, and manage user accounts

### Key Features
- 🔐 **Secure Authentication**: JWT-based authentication with role-based access control
- 📅 **Smart Scheduling**: Doctor availability management with time slot validation
- 📊 **Comprehensive Reporting**: Detailed analytics for administrators and doctors
- 🏥 **Healthcare-Specific**: Specialized fields for medical professionals (license numbers, specializations, consultation fees)
- 📱 **RESTful API**: Clean, well-documented API endpoints
- 🗄️ **Database Management**: Automated migrations with Alembic

## 🏗️ Architecture

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL with async SQLAlchemy
- **Authentication**: JWT tokens with bcrypt password hashing
- **Migrations**: Alembic for database schema management
- **File Storage**: Local file system for profile images
- **Validation**: Pydantic models for request/response validation

### Project Structure
```
appion/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── user.py            # User profile management
│   │   ├── doctor.py          # Doctor-specific operations
│   │   ├── appointment.py     # Appointment booking/management
│   │   ├── admin.py           # Admin operations
│   │   ├── dashboard.py       # Dashboard endpoints
│   │   └── _response.py       # Response formatting utilities
│   ├── core/                   # Core application logic
│   │   ├── config.py          # Environment configuration
│   │   ├── security.py        # JWT and password utilities
│   │   └── validators.py      # Input validation functions
│   ├── db/                     # Database configuration
│   │   ├── base.py            # SQLAlchemy base models
│   │   └── session.py         # Database session management
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py            # User model with role-based fields
│   │   └── appointment.py     # Appointment model
│   ├── schemas/                # Pydantic models for API
│   │   ├── user.py            # User request/response schemas
│   │   └── appointment.py     # Appointment schemas
│   ├── services/               # Business logic layer
│   │   ├── user.py            # User management services
│   │   ├── doctor.py          # Doctor-specific services
│   │   └── appointment.py     # Appointment services
│   └── alembic/               # Database migrations
├── static/                     # Static files (profile images)
├── requirements.txt            # Python dependencies
└── alembic.ini               # Alembic configuration
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.12 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd appion
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/appion_db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE appion_db;
   CREATE USER appion_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE appion_db TO appion_user;
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: multipart/form-data

{
  "full_name": "Dr. John Doe",
  "email": "doctor@example.com",
  "mobile": "+8801712345678",
  "password": "SecurePass123!",
  "role": "doctor",
  "division_id": 1,
  "district_id": 1,
  "thana_id": 1,
  "license_number": "DOC123456",
  "experience_years": 10,
  "consultation_fee": 500.0,
  "available_timeslots": "09:00-12:00,14:00-17:00",
  "specialization": "Cardiology"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

{
  "username": "doctor@example.com",
  "password": "SecurePass123!"
}
```

### Appointment Management

#### Book Appointment (Patient)
```http
POST /api/v1/appointments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "doctor_id": 1,
  "appointment_datetime": "2024-01-15T10:00:00",
  "notes": "Regular checkup",
  "symptoms": "Mild headache"
}
```

#### Update Appointment Status (Doctor)
```http
PATCH /api/v1/appointments/1/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "confirmed"
}
```

### Doctor Schedule Management

#### Update Doctor Schedule
```http
PUT /api/v1/doctors/schedule
Authorization: Bearer <token>
Content-Type: application/json

{
  "available_timeslots": "09:00-12:00,14:00-17:00",
  "consultation_fee": 600.0,
  "specialization": "Cardiology"
}
```

### Admin Operations

#### List All Appointments
```http
GET /api/v1/admin/appointments?skip=0&limit=10&status=pending
Authorization: Bearer <token>
```

#### Generate Doctor Report
```http
GET /api/v1/admin/reports/doctor/1?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

## 🗄️ Database Schema

### Users Table
The `users` table supports multiple roles with role-specific fields:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    mobile VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'admin', 'doctor', 'patient'
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Location fields
    division_id INTEGER,
    district_id INTEGER,
    thana_id INTEGER,
    
    -- Doctor-specific fields
    license_number VARCHAR(50),
    experience_years INTEGER,
    consultation_fee DECIMAL(10,2),
    available_timeslots TEXT, -- Comma-separated time slots
    specialization VARCHAR(100),
    
    -- Common fields
    profile_image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Appointments Table
```sql
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES users(id),
    doctor_id INTEGER REFERENCES users(id),
    appointment_datetime TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'confirmed', 'completed', 'cancelled'
    notes TEXT,
    symptoms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Key Design Decisions
- **Role-based schema**: Single users table with conditional fields based on role
- **Flexible scheduling**: Time slots stored as comma-separated strings for simplicity
- **Audit trails**: Created/updated timestamps on all tables
- **Status tracking**: Comprehensive appointment status management

## 🎯 Challenges & Assumptions

### Challenges Faced

1. **JSON Serialization Issues**
   - **Problem**: SQLAlchemy ORM objects and datetime objects not JSON serializable
   - **Solution**: Implemented Pydantic models with `from_orm()` for all API responses
   - **Impact**: Ensured consistent, serializable API responses

2. **Role-based Data Validation**
   - **Problem**: Different validation rules for different user roles
   - **Solution**: Implemented conditional validation in Pydantic models using validators
   - **Impact**: Maintained data integrity while supporting flexible user types

3. **Time Slot Management**
   - **Problem**: Complex scheduling logic with availability checks
   - **Solution**: Implemented time slot parsing and conflict detection
   - **Impact**: Reliable appointment booking with conflict prevention

4. **File Upload Security**
   - **Problem**: Secure handling of profile image uploads
   - **Solution**: Implemented file type validation, size limits, and secure storage
   - **Impact**: Protected against malicious file uploads

### Assumptions Made

1. **Geographic Structure**: Assumed Bangladesh's administrative structure (divisions, districts, thanas)
2. **Business Hours**: Default business hours of 08:00-18:00 for appointment booking
3. **Time Slots**: Doctor availability stored as simple time ranges (HH:MM-HH:MM)
4. **Consultation Duration**: Assumed 1-hour appointment slots with 1-minute buffer
5. **Mobile Numbers**: Bangladesh mobile number format (+88XXXXXXXXX)
6. **Password Policy**: Minimum 8 characters with uppercase, digit, and special character requirements

### Future Enhancements
- Real-time notifications using WebSockets
- Integration with external calendar systems
- Advanced reporting with data visualization
- Multi-language support
- Payment gateway integration
- Telemedicine features

## 🔧 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
- Type hints throughout the codebase
- Comprehensive error handling
- Input validation on all endpoints
- Consistent API response format

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

**Appion** - Streamlining healthcare appointment management for the modern world. 