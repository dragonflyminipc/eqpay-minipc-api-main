from datetime import datetime, timedelta
from service.clients import Bitcoin
from service.errors import Abort
from service import utils
import config

# Helper functions to format the response dict

def info(settings):
    client = Bitcoin(config.node_endpoint)
    result = {}

    result["node_address"] = settings.node_address

    if not (height := utils.get_height()):
        raise Abort("general", "internal-error")

    blockchain_info = client.make_request("getblockchaininfo", [])

    if blockchain_info["error"]:
        raise Abort("general", "internal-error")

    local_height = blockchain_info["result"]["blocks"]
    local_headers = blockchain_info["result"]["headers"]

    result["sync"] = {
        "synced": settings.synced,
        "local_headers": local_headers,
        "local_height": local_height,
        "height": height
    }

    wallet_info = client.make_request("getwalletinfo", [])

    if wallet_info["error"]:
        raise Abort("general", "internal-error")

    result["wallet"] = {
        "balance": wallet_info["result"]["balance"],
        "unconfirmed_balance": wallet_info["result"]["unconfirmed_balance"],
        "immature_balance": wallet_info["result"]["immature_balance"],
        "stake": wallet_info["result"]["stake"]
    }

    start_timestamp = None

    if settings.mining_start_timestamp and settings.staking_start_timestamp:
        start_timestamp = min(
            int(settings.mining_start_timestamp.timestamp()),
            int(settings.staking_start_timestamp.timestamp())
        )
    else:
        if settings.mining_start_timestamp:
            start_timestamp = int(settings.mining_start_timestamp.timestamp())
        elif settings.staking_start_timestamp:
            start_timestamp = int(settings.staking_start_timestamp.timestamp())

    coins_mined = utils.get_mined_coins(start_timestamp) if start_timestamp else 0

    result["mining"] = {
        "mining": settings.mining,
        "staking": settings.staking,
        "threads": settings.threads,
        "mining_start_timestamp": settings.mining_start_timestamp,
        "staking_start_timestamp": settings.staking_start_timestamp,
        "reward": coins_mined
    }

    scanning = wallet_info["result"]["scanning"] != False

    return result

def start_mining(settings):
    return {
        "mining_start_timestamp": settings.mining_start_timestamp,
        "mining": settings.mining,
        "threads": settings.threads
    }

def stop_mining(settings):
    time_spent_mining = timedelta(0)

    if settings.mining_start_timestamp:
        time_spent_mining = datetime.utcnow() - settings.mining_start_timestamp

    return {
        "time_spent_mining": int(time_spent_mining.total_seconds()),
        "mining": settings.mining,
        "threads": settings.threads
    }

def start_staking(settings):
    return {
        "staking_start_timestamp": settings.staking_start_timestamp,
        "staking": settings.staking,
    }

def stop_staking(settings):
    time_spent_staking = timedelta(0)

    if settings.staking_start_timestamp:
        time_spent_staking = datetime.utcnow() - settings.staking_start_timestamp

    return {
        "time_spent_staking": int(time_spent_staking.total_seconds()),
        "staking": settings.staking
    }
