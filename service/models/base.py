from sqlmodel import Field, SQLModel
from typing import Union

class BaseTable(SQLModel):
    id: Union[int, None] = Field(default=None, primary_key=True)
