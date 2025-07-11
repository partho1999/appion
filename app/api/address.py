from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from app.db.session import get_db
from app.models.address import Division, District, Thana
from sqlalchemy.future import select  # type: ignore

router = APIRouter(prefix="/api/address", tags=["address"])

@router.get("/divisions")
async def get_divisions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Division))
    return [d.name for d in result.scalars().all()]

@router.get("/districts/{division_id}")
async def get_districts(division_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(District).where(District.division_id == division_id))
    return [d.name for d in result.scalars().all()]

@router.get("/thanas/{district_id}")
async def get_thanas(district_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Thana).where(Thana.district_id == district_id))
    return [t.name for t in result.scalars().all()] 