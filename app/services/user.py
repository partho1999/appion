from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_mobile(db: AsyncSession, mobile: str):
    result = await db.execute(select(User).where(User.mobile == mobile))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate):
    hashed_password = get_password_hash(user_in.password)
    specialization = getattr(user_in, 'specialization', None)
    if specialization is not None:
        specialization = specialization.lower()
    # Save available_timeslots as-is (string), preserving formatting and spaces
    available_timeslots = getattr(user_in, 'available_timeslots', None)
    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        mobile=user_in.mobile,
        role=user_in.role,
        division_id=user_in.division_id,
        district_id=user_in.district_id,
        thana_id=user_in.thana_id,
        profile_image=user_in.profile_image,
        license_number=getattr(user_in, 'license_number', None),
        experience_years=getattr(user_in, 'experience_years', None),
        consultation_fee=getattr(user_in, 'consultation_fee', None),
        available_timeslots=available_timeslots,
        specialization=specialization,
        is_active=True,
        is_superuser=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 