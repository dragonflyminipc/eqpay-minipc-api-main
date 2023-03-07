from service.api.args import BaseArgs
from pydantic import Field

class WithdrawArgs(BaseArgs):
    address: str = Field(example="ERHutQiS2wRyrhZBzB3XSe8VeQQ9nDQhD6")
    amount: float = Field(example=3.08, gt=0)
