from pydantic import BaseModel, Field
from typing import Union

class InitArgs(BaseModel):
    mac_address: str = Field(example="af:4e:37:60:d5:6f")
    product_id: str = Field(example="some product id")
    user_id: str = Field(example="some user id")
    email: str = Field(example="example@gmail.com")
    passphrase: Union[str, None] = Field(default=None, example="565b5ac3012ecb37b77e402ecd0eaed9212026b1d71bcbc0afb38c5b1deb5844")
