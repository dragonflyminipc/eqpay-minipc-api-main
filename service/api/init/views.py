from sqlmodel.ext.asyncio.session import AsyncSession
from service.db import get_async_session
from .responses import InitResponse
from service.models import Settings
from service.clients import Bitcoin
from service.errors import Abort
from datetime import datetime
from fastapi import Depends
from sqlmodel import select
from ..views import router
from .args import InitArgs
from service import utils
import requests
import logging
import zipfile
import config
import json
import os

@router.post(
    "/init",
    tags=["Setup"],
    summary="Set up and start up an eqpay node",
    response_model=InitResponse
)
async def init(
    body: InitArgs,
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/init")

    if not utils.check_mac(body.mac_address):
        raise Abort("general", "wrong-mac")

    query = await session.exec(select(Settings))

    if not (settings := query.one_or_none()):
        settings = Settings()

    session.add(settings)
    await session.commit()
    await session.refresh(settings)

    if settings.initialised:
        raise Abort("init", "already-initialised")

    if settings.importing:
        raise Abort("general", "wallet-importing")

    if settings.exporting:
        raise Abort("general", "wallet-exporting")

    latest_release = requests.get(config.github_releases_endpoint)

    if latest_release.status_code != 200:
        logging.error(
            f"Github latest release returned status code {latest_release.status_code}"
        )
        raise Abort("init", "no-node-files")

    node_response = json.loads(latest_release.text)

    version = node_response["tag_name"]
    files = node_response["assets"]

    eqpay_node_download = None

    for file in files:
        if file["name"] == "eqpay-Linux.zip":
            eqpay_node_download = file["browser_download_url"]

    if not eqpay_node_download:
        logging.error(
            f"Github latest release didn't have the necessary download link\n"\
            f"{node_response}"
        )
        raise Abort("init", "no-node-files")

    node_zip_file = requests.get(eqpay_node_download)

    if node_zip_file.status_code != 200:
        logging.error(
            f"Node download returned status code {node_zip_file.status_code}"
        )
        raise Abort("init", "no-node-files")

    with open("node.zip", 'wb') as f:
        f.write(node_zip_file.content)

    with zipfile.ZipFile("node.zip") as z:
        z.extractall("node")

    if os.path.exists("node.zip"):
        os.remove("node.zip")

    # Loop through all the files of our zip and find the executable
    # Then move it to the bottom level of the folder

    node_executable_path = ""

    for subdir, dirs, files in os.walk("node/"):
        for file in files:
            filename = os.path.join(subdir, file)

            if config.node_executable in filename:
                if filename[-(len(config.node_executable)+1):] == config.node_executable:
                    os.rename(filename, f"node/{config.node_executable}")

    os.chmod(f"node/{config.node_executable}", 0o777)

    settings.node_version = version
    settings.init_timestamp = datetime.utcnow()
    settings.initialised = True
    settings.product_id = body.product_id
    settings.user_id = body.user_id
    settings.email = body.email
    settings.passphrase = body.passphrase

    logging.info("Successfully downloaded an eqpay node")

    await session.commit()
    await session.refresh(settings)

    return settings
