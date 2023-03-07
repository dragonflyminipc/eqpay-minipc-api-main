from pydantic import BaseModel, Field

class PasswordChangeResponse(BaseModel):
    message: str = Field(example="Changed wallet's passphrase")
