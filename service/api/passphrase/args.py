from service.api.args import BaseArgs
from pydantic import Field
from fastapi import Body

class ChangePassphraseArgs(BaseArgs):
    new_passphrase: str = Field(example="d5103ba4bf0fc85aed16605f8800ecb3f49475395135e7c6f9208d8d79ae5582")
