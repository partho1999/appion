import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.address import Division, District, Thana
from app.core.address_mapping import DIVISION_BN_TO_EN, DISTRICT_BN_TO_EN, THANA_BN_TO_EN

ADDRESS_JSON_PATH = os.path.join(os.path.dirname(__file__), '../static/addresses.json')

async def load_addresses_if_empty(db: AsyncSession):
    # Check if already loaded
    result = await db.execute(select(Division))
    if result.scalars().first():
        return
    # Load JSON
    with open(ADDRESS_JSON_PATH, encoding='utf-8') as f:
        data = json.load(f)
    for div_bn, districts in data.items():
        div_en = DIVISION_BN_TO_EN.get(div_bn, div_bn)
        division = Division(name=div_en)
        db.add(division)
        await db.flush()  # get division.id
        for dist_bn, dist_data in districts.items():
            dist_en = DISTRICT_BN_TO_EN.get(dist_bn, dist_bn)
            district = District(name=dist_en, division_id=division.id)
            db.add(district)
            await db.flush()  # get district.id
            for thana_bn in dist_data["উপজেলা"]:
                thana_en = THANA_BN_TO_EN.get(thana_bn, thana_bn)
                thana = Thana(name=thana_en, district_id=district.id)
                db.add(thana)
    await db.commit() 