from service.api.args import BaseArgs
from fastapi import Body

class StartMinerArgs(BaseArgs):
    threads: int = Body(default=32, le=1024, ge=1)
