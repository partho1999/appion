import os
from dotenv import load_dotenv  # type: ignore  # Ignore linter error if package is installed

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Appion Appointment Booking System"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:partho1234@localhost:5432/my_new_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

settings = Settings() 