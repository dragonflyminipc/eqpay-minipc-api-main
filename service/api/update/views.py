from sqlmodel.ext.asyncio.session import AsyncSession
from service.decorators import request_check
from service.db import get_async_session
from .responses import UpdateResponse
from service.models import Settings
from service.errors import Abort
from fastapi import Depends
from ..views import router
from .args import BaseArgs
from service import utils
import requests
import zipfile
import logging
import shutil
import config
import json
import os

@router.post(
    "/update",
    tags=["Update"],
    summary="Try to update the node",
    response_model=UpdateResponse
)
async def update(
    body: BaseArgs,
    settings: Settings = Depends(request_check),
    session: AsyncSession = Depends(get_async_session)
):
    logging.info("Request at /api/update")

    response = requests.get(config.github_releases_endpoint)

    if response.status_code != 200:
        logging.error(
            f"Github latest release returned status code {response.status_code}"
        )
        raise Abort("update", "no-node-files")

    response = json.loads(response.text)

    version = response["tag_name"]
    files = response["assets"]

    result = {
        "version": version,
        "updated": False
    }

    if version != settings.node_version:
        eqpay_node_download = None

        for file in files:
            if file["name"] == "eqpay-Linux.zip":
                eqpay_node_download = file["browser_download_url"]

        if not eqpay_node_download:
            logging.error(
            f"Github latest release didn't have the necessary download link\n"\
                f"{response}"
            )
            raise Abort("update", "no-node-files")

        response = requests.get(eqpay_node_download)

        if os.path.exists("node"):
            shutil.rmtree("node")

        with open("node.zip", 'wb') as f:
            f.write(response.content)

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

        utils.stop_node()

        settings.node_version = version

        result["updated"] = True

        logging.info("Successfully updated the node")

        await session.commit()

    return result
