from pydantic.datetime_parse import parse_datetime
from getmac import get_mac_address as gma
from service.clients import Bitcoin
from service.errors import Abort
from datetime import datetime
import requests
import config
import signal
import json
import os

class Datetime(int):
    @classmethod
    def __get_validators__(cls):
        yield parse_datetime
        yield cls.validate

    @classmethod
    def validate(cls, value) -> int:
        return int(value.timestamp())

def ping_rpc():
    client = Bitcoin(config.node_endpoint)
    response = client.make_request("getblockchaininfo", [])

    return response["error"] is None

def get_peers():
    url = "https://equitypay.online/data/peers"
    peers = []

    response = requests.get(url)

    if response.status_code != 200:
        return []

    response = json.loads(response.text)

    if response["error"]:
        return []

    datetime_format = "%a, %d %b %Y %H:%M:%S %Z"

    for peer in response["result"]:
        dt_object = datetime.strptime(peer["last"], datetime_format)
        delta = datetime.utcnow() - dt_object

        if delta.days >= 1:
            continue

        peers.append(peer)

    return peers

def get_mined_coins(after_timestamp):
    coins = 0

    client = Bitcoin(config.node_endpoint)

    response = client.make_request("listtransactions", ["*", 10000])

    for tx in response["result"]:
        if not "generated" in tx:
            continue

        if tx["generated"] != True:
            continue

        if tx["category"] == "orphan":
            continue

        if "blocktime" in tx and tx["blocktime"] < after_timestamp:
            continue

        coins += tx["amount"]

    return round(coins, 8)

def kill_process(name):
    for line in os.popen(f"ps ax | grep {name} | grep -v grep"):
        fields = line.split()
         
        # extracting Process ID from the output
        pid = fields[0]
         
        # terminating process
        os.kill(int(pid), signal.SIGKILL)

def stop_node():
    client = Bitcoin(config.node_endpoint)
    
    return client.make_request("stop", [])

def validate_address(address):
    # Basic address validation before doing the api check
    if not address or len(address) != 34:
        return False

    # Validate the address through an api
    address_check = requests.get(
        f"https://equitypay.online/balance/{address}"
    )

    if address_check.status_code != 200:
        return False

    data = json.loads(address_check.text)

    if data["error"]:
        return False

    return True

def check_mac(mac_address):
    return mac_address.replace("-", ":") == gma().replace("-", ":")

def get_height():
    response = requests.get("https://equitypay.online/info")

    if response.status_code != 200:
        return None

    response = json.loads(response.text)

    if response["error"]:
        return None

    return response["result"]["blocks"]

def check_wallet_import():
    client = Bitcoin(config.node_endpoint)

    wallet_info = client.make_request("getwalletinfo", [])

    if wallet_info["error"]:
        raise Abort("general", "internal-error")

    return wallet_info["result"]["scanning"] != False

def is_wallet_encrypted():
    client = Bitcoin(config.node_endpoint)

    respose = client.make_request("walletlock", [])

    if respose["error"]:
        return False

    return True

def check_passphrase(phrase):
    client = Bitcoin(config.node_endpoint)

    # Unlock for 60 seconds
    response = client.make_request("walletpassphrase", [phrase, 60])

    if response["error"]:
        return False

    return True
