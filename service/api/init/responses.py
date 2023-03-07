from pydantic import BaseModel, Field
from service.utils import Datetime
from typing import Union

class InitResponse(BaseModel):
    init_timestamp: Datetime = Field(example=1659766201)
    initialised: bool = Field(example=True)
    product_id: str = Field(example="some product id")
    user_id: str = Field(example="some user id")
    email: str = Field(example="example@gmail.com")

    class Config:
        orm_mode = True
