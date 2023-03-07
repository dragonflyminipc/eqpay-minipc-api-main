from pydantic import BaseModel, Field
from service.utils import Datetime
from typing import Union

class InfoSyncResponse(BaseModel):
    synced: bool = Field(example=True)
    local_headers: int = Field(example=30000)
    local_height: int = Field(example=30000)
    height: int = Field(example=30000)

class InfoWalletResponse(BaseModel):
    balance: float = Field(example=12.04)
    unconfirmed_balance: float = Field(example=0)
    immature_balance: float = Field(example=3.08)
    stake: float = Field(example=2.0)

class InfoMiningResponse(BaseModel):
    mining: bool = Field(example=True)
    staking: bool = Field(example=False)
    threads: int = Field(example=32)
    reward: float = Field(example=3.08)
    mining_start_timestamp: Union[Datetime, None] = Field(example=1659766201)
    staking_start_timestamp: Union[Datetime, None] = Field(example=1659766201)

class InfoResponse(BaseModel):
    node_address: Union[str, None] = Field(example="EZfbHSZ2EiSyS7xp1X6uzoJVxsyfjtsPP7")

    sync: InfoSyncResponse
    wallet: InfoWalletResponse
    mining: InfoMiningResponse
