from sqlalchemy.orm import declarative_base  # type: ignore  # Ignore linter error if package is installed

Base = declarative_base()

# Import all models here for Alembic autogeneration
from app.models import * 