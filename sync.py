from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging

def init_scheduler():
    scheduler = AsyncIOScheduler()

    from service.scheduler.generate_address import generate_address
    from service.scheduler.restart_mining import restart_mining
    from service.scheduler.check_sync import check_sync
    from service.scheduler.cache_info import cache_info
    from service.scheduler.add_peers import add_peers

    logging.basicConfig(
        filename="sync.log",
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.INFO
    )

    logging.getLogger(
        "apscheduler.executors.default"
    ).setLevel(logging.WARNING)

    scheduler.add_job(generate_address, "interval", minutes=1)
    scheduler.add_job(restart_mining,   "interval", minutes=5)
    scheduler.add_job(check_sync,       "interval", minutes=1)
    scheduler.add_job(cache_info,       "interval", minutes=1)
    scheduler.add_job(add_peers,        "interval", minutes=1)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    init_scheduler()
