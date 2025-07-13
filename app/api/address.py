from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from app.db.session import get_db
from app.models.address import Division, District, Thana
from sqlalchemy.future import select  # type: ignore
from typing import List, Dict

router = APIRouter(prefix="/api/address", tags=["address"])

@router.get("/divisions")
async def get_divisions(db: AsyncSession = Depends(get_db)):
    """Get all divisions with their IDs"""
    result = await db.execute(select(Division))
    divisions = result.scalars().all()
    return {
        "success": True,
        "data": [{"id": d.id, "name": d.name} for d in divisions],
        "count": len(divisions)
    }

@router.get("/districts/{division_id}")
async def get_districts(division_id: int, db: AsyncSession = Depends(get_db)):
    """Get all districts for a specific division"""
    # First verify the division exists
    division_result = await db.execute(select(Division).where(Division.id == division_id))
    division = division_result.scalar_one_or_none()
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    
    result = await db.execute(select(District).where(District.division_id == division_id))
    districts = result.scalars().all()
    return {
        "success": True,
        "data": [{"id": d.id, "name": d.name} for d in districts],
        "count": len(districts),
        "division": {"id": division.id, "name": division.name}
    }

@router.get("/upazilas/{district_id}")
async def get_upazilas(district_id: int, db: AsyncSession = Depends(get_db)):
    """Get all upazilas for a specific district"""
    # First verify the district exists
    district_result = await db.execute(select(District).where(District.id == district_id))
    district = district_result.scalar_one_or_none()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    result = await db.execute(select(Thana).where(Thana.district_id == district_id))
    upazilas = result.scalars().all()
    return {
        "success": True,
        "data": [{"id": u.id, "name": u.name} for u in upazilas],
        "count": len(upazilas),
        "district": {"id": district.id, "name": district.name}
    }

@router.get("/hierarchy")
async def get_address_hierarchy(db: AsyncSession = Depends(get_db)):
    """Get complete address hierarchy (divisions with their districts and upazilas)"""
    result = await db.execute(select(Division))
    divisions = result.scalars().all()
    
    hierarchy = []
    for division in divisions:
        division_data = {
            "id": division.id,
            "name": division.name,
            "districts": []
        }
        
        # Get districts for this division
        district_result = await db.execute(select(District).where(District.division_id == division.id))
        districts = district_result.scalars().all()
        
        for district in districts:
            district_data = {
                "id": district.id,
                "name": district.name,
                "upazilas": []
            }
            
            # Get upazilas for this district
            upazila_result = await db.execute(select(Thana).where(Thana.district_id == district.id))
            upazilas = upazila_result.scalars().all()
            
            district_data["upazilas"] = [{"id": u.id, "name": u.name} for u in upazilas]
            division_data["districts"].append(district_data)
        
        hierarchy.append(division_data)
    
    return {
        "success": True,
        "data": hierarchy,
        "total_divisions": len(hierarchy)
    }

@router.get("/division/{division_id}")
async def get_division_details(division_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific division with all its districts and upazilas"""
    division_result = await db.execute(select(Division).where(Division.id == division_id))
    division = division_result.scalar_one_or_none()
    
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    
    # Get districts for this division
    district_result = await db.execute(select(District).where(District.division_id == division.id))
    districts = district_result.scalars().all()
    
    division_data = {
        "id": division.id,
        "name": division.name,
        "districts": []
    }
    
    for district in districts:
        district_data = {
            "id": district.id,
            "name": district.name,
            "upazilas": []
        }
        
        # Get upazilas for this district
        upazila_result = await db.execute(select(Thana).where(Thana.district_id == district.id))
        upazilas = upazila_result.scalars().all()
        
        district_data["upazilas"] = [{"id": u.id, "name": u.name} for u in upazilas]
        division_data["districts"].append(district_data)
    
    return {
        "success": True,
        "data": division_data
    } 