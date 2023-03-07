from sqlmodel.ext.asyncio.session import AsyncSession
from service.db import async_engine
from service.models import Settings
from service.clients import Bitcoin
from sqlmodel import select
from .. import utils
import logging
import random
import config

MAX_PEERS = 4

# A routine to add peers to our node to speed up the syncing process
# It's run only once, after which the settings.added_peers flag is flipped
async def add_peers():
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

        # Already added peers
        if settings.added_peers:
            return

        peers = utils.get_peers()

        if len(peers) == 0:
            return

        # Pick random peers from list and add them
        for peer in random.sample(peers, min(len(peers), MAX_PEERS)):
            client.make_request("addnode", [peer["address"], "add"])

            logging.info(f"Added peer {peer['address']}")

        settings.added_peers = True
        await session.commit()
