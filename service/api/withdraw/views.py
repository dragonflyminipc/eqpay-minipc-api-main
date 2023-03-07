from sqlmodel.ext.asyncio.session import AsyncSession
from service.decorators import request_check
from service.db import get_async_session
from .responses import WithdrawResponse
from service.models import Settings
from service.clients import Bitcoin
from service.errors import Abort
from .args import WithdrawArgs
from fastapi import Depends
from ..views import router
from service import utils
import logging
import config

@router.post(
    "/withdraw",
    tags=["Withdraw"],
    summary="Send coins to a specified address",
    response_model=WithdrawResponse,
)
async def withdraw(
    body: WithdrawArgs,
    settings: Settings = Depends(request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/withdraw")
    client = Bitcoin(config.node_endpoint)

    wallet_info = client.make_request("getwalletinfo", [])

    if wallet_info["error"]:
        raise Abort("general", "internal-error")

    if wallet_info["result"]["balance"] < body.amount:
        raise Abort("withdraw", "bad-balance")

    if not utils.validate_address(body.address):
        raise Abort("withdraw", "invalid-address")

    result = client.make_request("sendtoaddress", 
        [body.address, body.amount, None, None, True]
    )

    if result["error"]:
        raise Abort("general", "internal-error")

    logging.info(f"Withdrew {body.amount} EQPAY to {body.address}")

    return {
        "address": body.address,
        "amount": body.amount
    }
