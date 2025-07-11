from sqlalchemy import Column, Integer, String, ForeignKey  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from app.db.base import Base

class Division(Base):
    __tablename__ = "divisions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    districts = relationship("District", back_populates="division")

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    division = relationship("Division", back_populates="districts")
    thanas = relationship("Thana", back_populates="district")

class Thana(Base):
    __tablename__ = "thanas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    district = relationship("District", back_populates="thanas") 