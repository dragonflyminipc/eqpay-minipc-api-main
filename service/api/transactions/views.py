from sqlmodel.ext.asyncio.session import AsyncSession
from .responses import TransactionListResponse
from service.db import get_async_session
from service.models import Settings
from service.clients import Bitcoin
from fastapi import Depends, Query
from service.errors import Abort
from sqlmodel import select
from ..views import router
from service import utils
from typing import Union
import logging
import config

@router.get(
   "/transactions",
    tags=["Transactions"],
    summary="Get a list of transactions",
    response_model=TransactionListResponse
)
async def transactions(
    mac_address: str = Query(example="af:4e:37:60:d5:6f"),
    passphrase: Union[str, None] = Query(default=None, example="d5103ba4bf0fc85aed16605f8800ecb3f49475395135e7c6f9208d8d79ae5582"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/transactions")

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

    client = Bitcoin(config.node_endpoint)

    # Get all transactions because we need to filter out the orpan ones
    response = client.make_request("listtransactions", [None, 999999, 0])

    if response["error"]:
        raise Abort("general", "internal-error")

    result = []

    skip = (page-1)*size
    count = size

    # Do wacky stuff because of orphan transactions
    for transaction in response["result"][::-1]:
        if transaction["category"] == "orphan":
            continue
        elif skip > 0:
            skip -= 1
            continue
        elif count > 0:
            count -= 1

            tx = transaction
            if tx["category"] == "generate":
                tx["category"] = "reward"

            result.append({
                "address": tx["address"],
                "category": tx["category"],
                "amount": tx["amount"],
                "blockhash": tx["blockhash"] if "blockhash" in tx else None,
                "blockheight": tx["blockheight"] if "blockheight" in tx else None,
                "timestamp": tx["time"],
                "txid": tx["txid"]
            })

        else:
            break

    return {
        "transactions": result,
        "page": page,
        "size": size,
        "count": len(result)
    }
