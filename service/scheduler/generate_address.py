from sqlmodel.ext.asyncio.session import AsyncSession
from service.db import async_engine
from service.models import Settings
from service.clients import Bitcoin
from sqlmodel import select
from .. import utils
import logging
import config

# A routine to generate a fixed address for the node
async def generate_address():
    async with AsyncSession(async_engine) as session:
        settings_query = await session.exec(select(Settings))

        if not (settings := settings_query.one_or_none()):
            return

        session.add(settings)
        await session.refresh(settings)

        # Haven't initialised the node yet
        if not settings.initialised:
            return

        # Haven't synced the node yet
        if not settings.synced:
            return

        client = Bitcoin(config.node_endpoint)

        # Node doesn't respond
        if not utils.ping_rpc():
            return

        # Already have a node address
        if settings.node_address:
            return

        get_result = client.make_request("getaddressesbylabel", ["node_main_address"])

        # No address under that label so we generate one
        if not get_result["result"]:
            create_result = client.make_request("getnewaddress", ["node_main_address"])

            logging.info(
                f"No address found, generating a new one: {create_result['result']}"
            )

            settings.node_address = create_result["result"]
        else:
            address = list(get_result["result"].keys())[0]

            logging.info(f"Found an address: {address}")

            settings.node_address = address

        await session.commit()
