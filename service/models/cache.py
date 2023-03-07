from datetime import datetime
from .base import BaseTable
from typing import Union

class Cache(BaseTable, table=True):
    __tablename__ = "service_cache"

    name: str
    cache: Union[str, None] = None
    timestamp: Union[datetime, None] = None
