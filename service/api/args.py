from pydantic import BaseModel, Field
from typing import Union

class BaseArgs(BaseModel):
    mac_address: str = Field(example="af:4e:37:60:d5:6f")
    passphrase: Union[str, None] = Field(default=None, example="565b5ac3012ecb37b77e402ecd0eaed9212026b1d71bcbc0afb38c5b1deb5844")
