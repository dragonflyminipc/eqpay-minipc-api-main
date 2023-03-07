from sqlmodel.ext.asyncio.session import AsyncSession
from service.db import async_engine
from service.models import Settings
from service.clients import Bitcoin
from sqlmodel import select
from .. import utils
import logging
import config

# A routine to restart the mining/staking if a node crashed for some reason
async def restart_mining():
    async with AsyncSession(async_engine) as session:
        settings_query = await session.exec(select(Settings))

        if not (settings := settings_query.one_or_none()):
            return

        session.add(settings)
        await session.refresh(settings)

        # Haven't initialised the node yet
        if not settings.initialised:
            return

        client = Bitcoin(config.node_endpoint)

        # Node doesn't respond
        if not utils.ping_rpc():
            return

        if settings.restart_mining:
            res = client.make_request("minerstart", [settings.threads])

            if not res["error"]:
                settings.restart_mining = False
                logging.info(f"Restarted mining with {settings.threads} threads")

        if settings.restart_staking:
            res = client.make_request("stakerstart", [])

            if not res["error"]:
                settings.restart_staking = False
                logging.info(f"Restarted stacking")

        await session.commit()
