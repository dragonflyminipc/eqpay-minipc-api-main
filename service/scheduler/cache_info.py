from sqlmodel.ext.asyncio.session import AsyncSession
from service.models import Settings, Cache
from service.db import async_engine
from datetime import datetime
from sqlmodel import select
from .. import display
import json

async def cache_info():
    async with AsyncSession(async_engine) as session:
        settings_query = await session.exec(select(Settings))

        if not (settings := settings_query.one_or_none()):
            return

        session.add(settings)
        await session.refresh(settings)

        if not settings.initialised:
            return

        cache_query = await session.exec(
            select(Cache).where(Cache.name == "info")
        )

        if not (cache := cache_query.one_or_none()):
            cache = Cache(name="info")

        info = display.info(settings)

        info["mining"]["mining_start_timestamp"] = info["mining"][
            "mining_start_timestamp"
        ].timestamp() if info["mining"]["mining_start_timestamp"] else None

        info["mining"]["staking_start_timestamp"] = info["mining"][
            "staking_start_timestamp"
        ].timestamp() if info["mining"]["staking_start_timestamp"] else None

        cache.cache = json.dumps(info)
        cache.timestamp = datetime.utcnow()

        session.add(cache)
        await session.commit()
        await session.refresh(cache)
