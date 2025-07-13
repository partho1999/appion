import re
from fastapi import HTTPException, UploadFile
from datetime import datetime
from typing import List

PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$')
MOBILE_REGEX = re.compile(r'^\+88\d{11}$')
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]
MAX_IMAGE_SIZE_MB = 5

def validate_password(password: str):
    if not PASSWORD_REGEX.match(password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters, include 1 uppercase, 1 digit, 1 special character.")

def validate_mobile(mobile: str):
    if not MOBILE_REGEX.match(mobile):
        raise HTTPException(status_code=400, detail="Mobile number must start with +88 and be exactly 14 digits.")

def validate_image(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Profile image must be JPEG or PNG.")
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Profile image must be ≤{MAX_IMAGE_SIZE_MB}MB.")

def validate_timeslots(timeslots: List[str]):
    """Validate doctor timeslots format"""
    if not timeslots:
        raise HTTPException(status_code=400, detail="At least one timeslot must be provided.")
    
    for timeslot in timeslots:
        if not isinstance(timeslot, str) or '-' not in timeslot:
            raise HTTPException(status_code=400, detail="Timeslots must be in format 'HH:MM-HH:MM'.")
        
        try:
            start_str, end_str = timeslot.split('-')
            start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
            end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
            
            if start_time >= end_time:
                raise HTTPException(status_code=400, detail="Start time must be before end time.")
            
            # Validate business hours (8 AM to 6 PM)
            business_start = datetime.strptime('08:00', '%H:%M').time()
            business_end = datetime.strptime('18:00', '%H:%M').time()
            
            if start_time < business_start or end_time > business_end:
                raise HTTPException(status_code=400, detail="Timeslots must be within business hours (08:00-18:00).")
                
        except ValueError:
            raise HTTPException(status_code=400, detail="Timeslots must be in format 'HH:MM-HH:MM'.")

def validate_appointment_time(appointment_datetime: datetime):
    """Validate appointment time is in the future and within business hours"""
    now = datetime.now()
    if appointment_datetime < now:
        raise HTTPException(status_code=400, detail="Appointment cannot be in the past.")
    
    appointment_time = appointment_datetime.time()
    business_start = datetime.strptime('08:00', '%H:%M').time()
    business_end = datetime.strptime('18:00', '%H:%M').time()
    
    if not (business_start <= appointment_time <= business_end):
        raise HTTPException(status_code=400, detail="Appointment must be within business hours (08:00-18:00).") 