from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging

def init_scheduler():
    scheduler = AsyncIOScheduler()

    from service.scheduler.start_node import start_node

    logging.basicConfig(
        filename="node.log",
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.INFO
    )

    logging.getLogger(
        "apscheduler.executors.default"
    ).setLevel(logging.WARNING)

    scheduler.add_job(start_node, "interval", minutes=1)

    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    init_scheduler()
