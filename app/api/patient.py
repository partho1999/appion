from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from app.db.session import get_db
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from typing import Optional
from app.api._response import envelope_endpoint

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])

@router.get("/")
@envelope_endpoint
async def list_patients(
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    query = select(User).where(User.role == UserRole.patient)
    if search:
        query = query.where(User.full_name.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all() 