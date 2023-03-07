from .responses import StartStakingResponse, StopStakingResponse
from .responses import StartMinerResponse, StopMinerResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from service.decorators import request_check
from .args import StartMinerArgs, BaseArgs
from service.db import get_async_session
from datetime import datetime, timedelta
from service.models import Settings
from service.clients import Bitcoin
from service.errors import Abort
from service import display
from fastapi import Depends
from ..views import router
import logging
import config

@router.post(
    "/miner/start",
    tags=["Mining"],
    summary="Start mining",
    response_model=StartMinerResponse
)
async def start(
    body: StartMinerArgs,
    settings: Settings = Depends(request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/miner/start")
    if not settings.synced:
        raise Abort("general", "not-synced")

    client = Bitcoin(config.node_endpoint)

    response = client.make_request("minerstart", [body.threads])

    if response["error"]:
        raise Abort("general", "internal-error")

    settings.threads = body.threads
    settings.mining = True

    if not settings.mining_start_timestamp:
        settings.mining_start_timestamp = datetime.utcnow()

    logging.info(f"Started mining with {body.threads} threads")

    await session.commit()
    await session.refresh(settings)

    return display.start_mining(settings)

@router.post(
    "/miner/stop",
    tags=["Mining"],
    summary="Stop mining",
    response_model=StopMinerResponse
)
async def stop(
    body: BaseArgs,
    settings: Settings = Depends(request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/miner/stop")
    if not settings.synced:
        raise Abort("general", "not-synced")

    client = Bitcoin(config.node_endpoint)

    response = client.make_request("minerstop", [])

    if response["error"]:
        raise Abort("general", "internal-error")

    settings.threads = 0
    settings.mining = False
    settings.mining_start_timestamp = None

    logging.info("Stopped mining")

    await session.commit()
    await session.refresh(settings)

    return display.stop_mining(settings)

@router.post(
    "/staking/start",
    tags=["Staking"],
    summary="Start staking",
    response_model=StartStakingResponse
)
async def start(
    body: BaseArgs,
    settings: Settings = Depends(request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/staking/start")
    if not settings.synced:
        raise Abort("general", "not-synced")

    client = Bitcoin(config.node_endpoint)

    response = client.make_request("stakerstart", [])

    if response["error"]:
        raise Abort("general", "internal-error")

    settings.staking = True

    if not settings.staking_start_timestamp:
        settings.staking_start_timestamp = datetime.utcnow()

    logging.info("Started staking")

    await session.commit()
    await session.refresh(settings)

    return display.start_staking(settings)

@router.post(
    "/staking/stop",
    tags=["Staking"],
    summary="Stop staking",
    response_model=StopStakingResponse
)
async def stop(
    body: BaseArgs,
    settings: Settings = Depends(request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/staking/stop")
    if not settings.synced:
        raise Abort("general", "not-synced")

    client = Bitcoin(config.node_endpoint)

    response = client.make_request("stakerstop", [])

    if response["error"]:
        raise Abort("general", "internal-error")

    settings.staking = False
    settings.staking_start_timestamp = None

    logging.info("Stopped staking")

    await session.commit()
    await session.refresh(settings)

    return display.stop_staking(settings)
