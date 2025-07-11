from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from app.db.session import get_db
from app.models.user import User, UserRole
from typing import Optional
from app.api._response import envelope_endpoint

router = APIRouter(prefix="/api/v1/doctors", tags=["doctors"])

@router.get("/")
@envelope_endpoint
async def list_doctors(
    specialization: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
    division_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    thana_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.role == UserRole.doctor)
    if specialization:
        query = query.where(User.specialization == specialization)
    if division_id:
        query = query.where(User.division_id == division_id)
    if district_id:
        query = query.where(User.district_id == district_id)
    if thana_id:
        query = query.where(User.thana_id == thana_id)
    if search:
        query = query.where(User.full_name.ilike(f"%{search}%"))
    # TODO: Implement availability logic if needed
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all() 