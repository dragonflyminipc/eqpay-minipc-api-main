from service.api.args import BaseArgs
from pydantic import Field, BaseModel

class WithdrawResponse(BaseModel):
    address: str = Field(example="ERHutQiS2wRyrhZBzB3XSe8VeQQ9nDQhD6")
    amount: float = Field(example=3.08)
