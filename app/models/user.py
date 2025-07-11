from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float  # type: ignore
from sqlalchemy.sql import func  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    patient = "patient"
    doctor = "doctor"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    mobile = Column(String, unique=True, nullable=False)
    profile_image = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.patient)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    thana_id = Column(Integer, ForeignKey("thanas.id"), nullable=True)
    division = relationship("Division")
    district = relationship("District")
    thana = relationship("Thana")
    # Doctor-specific fields
    license_number = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    consultation_fee = Column(Float, nullable=True)
    available_timeslots = Column(String, nullable=True)  # Store as JSON string or comma-separated
    specialization = Column(String, nullable=True)  # Doctor specialization
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 