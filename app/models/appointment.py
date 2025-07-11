from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.sql import func  # type: ignore
from app.db.base import Base
import enum

class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_datetime = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    symptoms = Column(String, nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id]) 