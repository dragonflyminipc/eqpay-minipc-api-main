from sqlmodel.ext.asyncio.session import AsyncSession
from service.db import async_engine
from service.models import Settings
from service.clients import Bitcoin
from sqlmodel import select
from .. import utils
import requests
import logging
import config
import json

eqpay_chaininfo_api = "https://equitypay.online/info"

# A routine to check the sync status of the node
# It's run only once, after which the settings.synced flag is flipped
async def check_sync():
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

        response = requests.get(eqpay_chaininfo_api)

        if response.status_code != 200:
            return

        response = json.loads(response.text)

        if response["error"]:
            return

        height = response["result"]["blocks"]

        response = client.make_request("getblockchaininfo", [])

        if response["error"]:
            return

        local_height = response["result"]["blocks"]
        local_headers = response["result"]["headers"]

        # Note: 100 here is an arbitrary number, it just needs to be
        # decently larger than 0
        if local_height == height and\
            local_headers == height and\
            local_height > 100 and\
            height > 100 and\
            not settings.synced:

            settings.synced = True

            logging.info(
                f"Finished syncing: local_height={local_height}, "\
                f"local_headers={local_headers}, height={height}"
            )

            if settings.passphrase and not settings.encrypted_wallet:
                response = client.make_request("encryptwallet", [settings.passphrase])

                if not response["error"]:
                    settings.passphrase = None
                    settings.encrypted_wallet = True

                    logging.info(f"Encrypted the wallet with a passphrase")

            await session.commit()
