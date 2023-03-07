from datetime import datetime
from .base import BaseTable
from typing import Union

# Variables used to represent the internal state of the miner
class Settings(BaseTable, table=True):
    __tablename__ = "service_settings"

    node_version: str = "0.0.0"

    mining_start_timestamp: Union[datetime, None] = None
    staking_start_timestamp: Union[datetime, None] = None
    init_timestamp: Union[datetime, None] = None

    # Used for initialization
    initialised: bool = False
    added_peers: bool = False
    synced: bool = False

    # State of the miner
    staking: bool = False
    mining: bool = False
    threads: int = 0

    # This node's fixed address
    node_address: Union[str, None] = None

    # State of the node during a restart
    importing: bool = False
    exporting: bool = False
    wallet_id: Union[str, None] = None

    # Used in case a node crashed to restart the mining/staking
    restart_staking: bool = False
    restart_mining: bool = False

    # Auth/user related variables
    product_id: Union[str, None] = None
    user_id: Union[str, None] = None
    email: Union[str, None] = None

    # Temporarily store the passphrase while it's syncing
    encrypted_wallet: bool = False
    passphrase: Union[str, None] = None
