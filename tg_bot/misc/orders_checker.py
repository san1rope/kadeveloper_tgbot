import asyncio
import logging

from tg_bot.db_models.db_gino import connect_to_db
from tg_bot.db_models.quick_commands import DbOrder

logger = logging.getLogger(__name__)


async def start_orders_checker():
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

    await connect_to_db(remove_data=False)
    logger.info("Orders checker has been started!")

    while True:
        await asyncio.sleep(10)

        db_orders = await DbOrder(status=0).select()
        for order in db_orders:
            pass
