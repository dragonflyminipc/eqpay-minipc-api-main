from sqlmodel.ext.asyncio.session import AsyncSession
from service.db import async_engine
from service.models import Settings
from sqlmodel import select
import subprocess
import logging
import config
import shlex
import time

process = None

# A routine to start/restart the node if it crashed for some reason
async def start_node():
    global process

    async with AsyncSession(async_engine) as session:
        settings_query = await session.exec(select(Settings))

        if not (settings := settings_query.one_or_none()):
            return

        session.add(settings)
        await session.refresh(settings)

        # Haven't initialised the node yet
        if not settings.initialised:
            return

        # We stopped the node intentionally to import/export the wallet
        if settings.importing or settings.exporting:
            # Wait 5 seconds in case this runs instantly after
            # we start importing/exporting the wallet
            time.sleep(5)

            logging.info(
                f"Resetting the importing/exporting flag: "\
                f"importing: {settings.importing}, "\
                f"exporting: {settings.exporting}"
            )

            settings.importing = False
            settings.exporting = False

        command_extension = ""

        if settings.wallet_id:
            command_extension = f" -wallet={settings.wallet_id}"

        # First run, process doesn't exist yet
        if not process:
            logging.info(
                f"First run. Starting the process. "\
                f"mining: {settings.mining}, "\
                f"staking: {settings.staking}, "\
                f"command: {config.run_node_command + command_extension}"
            )

            settings.restart_staking = settings.staking
            settings.restart_mining = settings.mining

            await session.commit()

            process = subprocess.Popen(shlex.split(
                config.run_node_command + command_extension
            ))
            return

        # Our process is still running
        if process.poll() is None:
            return
        
        # Our process closed so we run it again
        logging.info(
            f"Process terminated, restarting. "\
            f"mining: {settings.mining}, "\
            f"staking: {settings.staking}, "\
            f"command: {config.run_node_command + command_extension}"
        )

        settings.restart_staking = settings.staking
        settings.restart_mining = settings.mining

        await session.commit()

        process = subprocess.Popen(shlex.split(
            config.run_node_command + command_extension
        ))
