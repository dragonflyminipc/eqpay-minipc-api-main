from sqlmodel.ext.asyncio.session import AsyncSession
from .responses import PasswordChangeResponse
from service.decorators import request_check
from service.db import get_async_session
from datetime import datetime, timedelta
from .args import ChangePassphraseArgs
from service.models import Settings
from service.clients import Bitcoin
from service.errors import Abort
from fastapi import Depends
from ..views import router
from service import utils
import logging
import config

@router.post(
    "/passphrase/change",
    tags=["Passphrase"],
    summary="Change (set if didn't already) the passphrase",
    response_model=PasswordChangeResponse
)
async def change(
    body: ChangePassphraseArgs,
    settings: Settings = Depends(request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/passphrase/change")
    if not settings.synced:
        raise Abort("general", "not-synced")

    client = Bitcoin(config.node_endpoint)

    # First time encrypting
    if not utils.is_wallet_encrypted():
        result = client.make_request("encryptwallet", [body.new_passphrase])

        if result["error"]:
            raise Abort("passphrase", "couldnt-encrypt")

        logging.info("Encrypted wallet for the first time")

        settings.encrypted_wallet = True
        settings.passphrase = None
    # Changing the passphrase
    else:
        result = client.make_request("walletpassphrasechange", [body.passphrase, body.new_passphrase])

        if result["error"]:
            raise Abort("passphrase", "couldnt-change-phrase")

        logging.info("Changed wallet's passphrase")

    await session.commit()
    await session.refresh(settings)

    return {
        "message": "Changed wallet's passphrase"
    }
