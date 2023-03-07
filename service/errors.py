from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import Request
import logging

class ErrorResponse(BaseModel):
    message: str = Field(example="Example error message")
    code: str = Field(example="example_error")

errors = {
    "general": {
        "wrong-mac": ["Wrong mac address", 400],
        "wrong-product-id": ["Wrong product id", 400],
        "not-initialised": ["Node not initialised", 400],
        "not-synced": ["Node isn't fully synced yet", 400],
        "internal-error": ["Service couldn't get the necessary data. Api or node is probably down", 500],
        "couldnt-read-file": ["There was an error uploading the file", 400],
        "wallet-importing": ["A wallet is currently being imported", 400],
        "wallet-exporting": ["A wallet is currently being exported", 400],
        "invalid-passphrase": ["Invalid passphrase", 400],
    },
    "init": {
        "already-initialised": ["Already initialised", 400],
        "no-node-files": ["Couldn't download node files", 500],
    },
    "update": {
        "no-node-files": ["Couldn't get the node files", 500],
    },
    "withdraw": {
        "bad-balance": ["Not enough balance to make the withdrawal", 400],
        "invalid-address": ["Invalid address", 400],
    },
    "passphrase": {
        "couldnt-encrypt": ["Couldn't encrypt the wallet", 500],
        "couldnt-change-phrase": ["Couldn't change the passphrase", 500],
    },
    "wallet": {
        "doesnt-exist": ["The wallet.dat file doesn't exist yet", 400],
        "couldnt-stop-node": ["Couldn't safely stop the node, please try again later", 500],
    }
}

class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message

async def abort_handler(request: Request, exc: Abort):
    error_code = exc.scope.replace("-", "_") + "_" + exc.message.replace("-", "_")

    try:
        error_message = errors[exc.scope][exc.message][0]
        status_code = errors[exc.scope][exc.message][1]
    except Exception:
        error_message = "Unknown error"
        status_code = 400

    logging.warning(f"Abort at {request.url.path}: {error_message}, {error_code}")

    return JSONResponse(
        content={"error": {
            "message": error_message, "code": error_code
        }, "data": {}},
        status_code=status_code
    )

async def validation_handler(request: Request, exc: RequestValidationError):
    exc_str = str(exc).replace("\n", " ").replace("   ", " ")
    return JSONResponse(
        content={"error": {
            "message": exc_str, "code": "validation_error"
        }, "data": {}},
        status_code=422
    )
