from sqlmodel.ext.asyncio.session import AsyncSession
from service.models import Settings, Cache
from service.db import get_async_session
from .responses import InfoResponse
from fastapi import Depends, Query
from service.errors import Abort
from datetime import datetime
from sqlmodel import select
from service import display
from ..views import router
from service import utils
from typing import Union
import logging
import json

@router.get(
    "/info",
    tags=["Info"],
    summary="Get node and mining info",
    response_model=InfoResponse
)
async def info(
    mac_address: str = Query(example="af:4e:37:60:d5:6f"),
    passphrase: Union[str, None] = Query(default=None, example="d5103ba4bf0fc85aed16605f8800ecb3f49475395135e7c6f9208d8d79ae5582"),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/info")

    if not utils.check_mac(mac_address):
        raise Abort("general", "wrong-mac")

    if utils.is_wallet_encrypted():
        if not utils.check_passphrase(passphrase):
            raise Abort("general", "invalid-passphrase")

    settings_query = await session.exec(select(Settings))

    if not (settings := settings_query.one_or_none()):
        settings = Settings()

    session.add(settings)
    await session.commit()
    await session.refresh(settings)

    if not settings.initialised:
        raise Abort("general", "not-initialised")

    if settings.importing:
        raise Abort("general", "wallet-importing")

    if settings.exporting:
        raise Abort("general", "wallet-exporting")

    cache_query = await session.exec(
        select(Cache).where(Cache.name == "info")
    )

    if settings.synced:
        logging.info("/api/info uncached response")
        return display.info(settings)

    # Cache only when syncing
    result = {}

    if not (cache := cache_query.one_or_none()):
        logging.info("/api/info no cache")

        result = display.info(settings)
        result["mining"]["mining_start_timestamp"] = result["mining"][
            "mining_start_timestamp"
        ].timestamp() if result["mining"]["mining_start_timestamp"] else None

        result["mining"]["staking_start_timestamp"] = result["mining"][
            "staking_start_timestamp"
        ].timestamp() if result["mining"]["staking_start_timestamp"] else None

        json_string = json.dumps(result)

        cache = Cache(
            name="info",
            cache=json_string,
            timestamp=datetime.utcnow()
        )

    if (datetime.utcnow() - cache.timestamp).seconds > 60:
        logging.info(
            f"/api/info expired cache: {(datetime.utcnow() - cache.timestamp).seconds}"
        )

        result = display.info(settings)
        result["mining"]["mining_start_timestamp"] = result["mining"][
            "mining_start_timestamp"
        ].timestamp() if result["mining"]["mining_start_timestamp"] else None

        result["mining"]["staking_start_timestamp"] = result["mining"][
            "staking_start_timestamp"
        ].timestamp() if result["mining"]["staking_start_timestamp"] else None

        json_string = json.dumps(result)

        cache.cache = json_string
        cache.timestamp=datetime.utcnow()

    session.add(cache)
    await session.commit()
    await session.refresh(cache)

    if not result:
        logging.info("/api/info cached response")
        result = json.loads(cache.cache)

    result["mining"]["mining_start_timestamp"] = datetime.utcfromtimestamp(result["mining"][
        "mining_start_timestamp"
    ]) if result["mining"]["mining_start_timestamp"] else None

    result["mining"]["staking_start_timestamp"] = datetime.utcfromtimestamp(result["mining"][
        "staking_start_timestamp"
    ]) if result["mining"]["staking_start_timestamp"] else None
    return result
