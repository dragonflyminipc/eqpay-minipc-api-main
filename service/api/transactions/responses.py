from pydantic import BaseModel, Field
from service.utils import Datetime
from typing import List, Union

class TransactionResponse(BaseModel):
    address: str = Field(example="EXgoT8c8ZdK88dvZuTEVFRHkqqHK6ytLvZ")
    category: str = Field(example="reward")
    amount: float = Field(example=1.87)
    blockhash: Union[str, None] = Field(example="f75e2c6a0da8c0ba990907e0c72145f00abbcc0a7808f86f099cc5f1347751a3")
    blockheight: Union[int, None] = Field(example=833442)
    timestamp: Datetime = Field(example=1676885527)
    txid: str = Field(example="0e40f110ab4976cbfdcac78f72e95b6b830a3cd879851f133550885ff4294f10")

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]

    page: int = Field(example=1)
    size: int = Field(example=10)
    count: int = Field(example=10)
