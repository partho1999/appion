import re
from fastapi import HTTPException, UploadFile

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