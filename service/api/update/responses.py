from pydantic import BaseModel, Field

class UpdateResponse(BaseModel):
    updated: bool = Field(example=True)
    version: str = Field(example="1.0.0")
