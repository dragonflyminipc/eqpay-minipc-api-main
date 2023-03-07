from sqlmodel.ext.asyncio.session import AsyncSession
from getmac import get_mac_address as gma
from fastapi import Depends, Body, Form
from service.api.args import BaseArgs
from .db import get_async_session
from .models import Settings
from sqlmodel import select
from .errors import Abort
from service import utils
from typing import Union

async def request_check(
    body: BaseArgs,
    session: AsyncSession = Depends(get_async_session),
) -> Settings:
    if not utils.check_mac(body.mac_address):
        raise Abort("general", "wrong-mac")

    query = await session.exec(select(Settings))

    if not (settings := query.one_or_none()):
        settings = Settings()

    session.add(settings)
    await session.commit()
    await session.refresh(settings)

    if not utils.ping_rpc():
        raise Abort("general", "internal-error")

    if not settings.initialised:
        raise Abort("general", "not-initialised")

    if settings.importing:
        raise Abort("general", "wallet-importing")

    if settings.exporting:
        raise Abort("general", "wallet-exporting")

    if utils.is_wallet_encrypted():
        if not utils.check_passphrase(body.passphrase):
            raise Abort("general", "invalid-passphrase")

    return settings

async def bodyless_request_check(
    mac_address: str = Form(...),
    passphrase: Union[str, None] = Form(...),
    session: AsyncSession = Depends(get_async_session),
) -> Settings:
    if not utils.check_mac(mac_address):
        raise Abort("general", "wrong-mac")

    query = await session.exec(select(Settings))

    if not (settings := query.one_or_none()):
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

    if utils.is_wallet_encrypted():
        if not utils.check_passphrase(passphrase):
            raise Abort("general", "invalid-passphrase")

    return settings
