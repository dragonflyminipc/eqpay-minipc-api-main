from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import fastapi.openapi.utils as fu
from fastapi import FastAPI
from .db import init_db
from . import errors
import logging
import config

def create_app() -> FastAPI:
    fu.validation_error_response_definition = errors.ErrorResponse.schema()

    logging.basicConfig(
        filename="api.log",
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.INFO
    )

    if config.debug:
        app = FastAPI()
    else:
        app = FastAPI(docs_url=None, redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, errors.validation_handler)
    app.add_exception_handler(errors.Abort, errors.abort_handler)

    from .api import api

    app.include_router(api)

    @app.on_event("startup")
    async def on_startup():
        await init_db()

    return app
