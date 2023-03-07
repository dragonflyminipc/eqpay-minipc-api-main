from pydantic import BaseModel, Field
from service.utils import Datetime

class StartMinerResponse(BaseModel):
    mining_start_timestamp: Datetime = Field(example=1659766201)
    mining: bool = Field(example=True)
    threads: int = Field(example=32)

class StopMinerResponse(BaseModel):
    time_spent_mining: int = Field(example=70)
    mining: bool = Field(example=False)
    threads: int = Field(example=0)

class StartStakingResponse(BaseModel):
    staking_start_timestamp: Datetime = Field(example=1659766201)
    staking: bool = Field(example=True)

class StopStakingResponse(BaseModel):
    time_spent_staking: int = Field(example=70)
    staking: bool = Field(example=False)
