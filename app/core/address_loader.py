import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.address import Division, District, Thana

ADDRESS_JSON_PATH = os.path.join(os.path.dirname(__file__), '../static/addresses.json')

async def load_addresses_if_empty(db: AsyncSession):
    # Check if already loaded
    result = await db.execute(select(Division))
    if result.scalars().first():
        return
    
    # Load JSON
    with open(ADDRESS_JSON_PATH, encoding='utf-8') as f:
        data = json.load(f)
    
    for division_name, districts in data.items():
        division = Division(name=division_name)
        db.add(division)
        await db.flush()  # get division.id
        
        for district_name, district_data in districts.items():
            district = District(name=district_name, division_id=division.id)
            db.add(district)
            await db.flush()  # get district.id
            
            for upazila_name in district_data["Upazila"]:
                thana = Thana(name=upazila_name, district_id=district.id)
                db.add(thana)
    
    await db.commit() 