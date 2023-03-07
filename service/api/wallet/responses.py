from pydantic import BaseModel, Field

class WalletImportResponse(BaseModel):
    message: str = Field(example="Started the process of wallet importing")
