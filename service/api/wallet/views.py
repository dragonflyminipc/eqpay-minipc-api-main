from fastapi import Depends, BackgroundTasks, File, UploadFile, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from service.decorators import bodyless_request_check
from .responses import WalletImportResponse
from fastapi.responses import FileResponse
from service.db import get_async_session
from service.models import Settings
from service.clients import Bitcoin
from service.errors import Abort
from sqlmodel import select
from ..views import router
from .args import BaseArgs
from service import utils
from typing import Union
import logging
import secrets
import config
import os

@router.get(
    "/wallet/export",
    tags=["Wallet"],
    summary="Export the wallet file. The node will have to stop and then will restart automatically",
    response_class=FileResponse,
)
async def export_wallet(
    background_tasks: BackgroundTasks,
    mac_address: str = Query(example="af:4e:37:60:d5:6f"),
    passphrase: Union[str, None] = Query(default=None, example="d5103ba4bf0fc85aed16605f8800ecb3f49475395135e7c6f9208d8d79ae5582"),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/wallet/export")
    if not utils.check_mac(mac_address):
        raise Abort("general", "wrong-mac")

    if utils.is_wallet_encrypted():
        if not utils.check_passphrase(passphrase):
            raise Abort("general", "invalid-passphrase")

    query = await session.exec(select(Settings))

    if not (settings := query.one_or_none()):
        settings = Settings()

    if settings.importing:
        raise Abort("general", "wallet-importing")

    if settings.exporting:
        raise Abort("general", "wallet-exporting")

    client = Bitcoin(config.node_endpoint)

    wallet_path = "~/.eqpay/wallets/wallet.dat"

    if settings.wallet_id:
        wallet_path = f"~/.eqpay/wallets/{settings.wallet_id}/wallet.dat"

    wallet_path = os.path.expanduser(wallet_path)

    if not os.path.exists(wallet_path):
        raise Abort("wallet", "doesnt-exist")
 
    response = client.make_request("stop", [])

    if response["error"]:
        raise Abort("general", "couldnt-stop-node")

    settings.exporting = True

    session.add(settings)
    await session.commit()
    await session.refresh(settings)

    logging.info("Started exporting the wallet")

    return FileResponse(
        wallet_path,
        media_type="application/octet-stream",
        filename="wallet.dat"
    )

@router.post(
    "/wallet/import",
    tags=["Wallet"],
    summary="Import the wallet file. It will stop the node which will restart automatically and stop mining/staking.",
    response_model=WalletImportResponse,
)
async def import_wallet(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    settings: Settings = Depends(bodyless_request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/wallet/import")
    wallet_id = str(secrets.token_hex(8))
    file_path = f"~/.eqpay/wallets/{wallet_id}/wallet.dat"
   
    file_path = os.path.expanduser(file_path)

    try:
        contents = file.file.read()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as wallet:
            wallet.write(contents)
    except Exception:
        raise Abort("general", "couldnt-read-file")
    finally:
        file.file.close()

    client = Bitcoin(config.node_endpoint)

    response = client.make_request("stop", [])

    if response["error"]:
        raise Abort("general", "couldnt-stop-node")

    settings.importing = True
    settings.wallet_id = wallet_id

    settings.staking = False
    settings.mining = False
    settings.threads = 0

    settings.node_address = None

    settings.mining_start_timestamp = None
    settings.staking_start_timestamp = None

    logging.info(f"Started importing the wallet with id {wallet_id}")

    await session.commit()
    await session.refresh(settings)

    return {
        "message": "Started the process of wallet importing"
    }
