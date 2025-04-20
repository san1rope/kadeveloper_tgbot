import asyncio
import logging

from tg_bot.db_models.db_gino import connect_to_db
from tg_bot.db_models.quick_commands import DbOrder
from tg_bot.misc.api_interface import APIInterface
from tg_bot.misc.models import APIUser

logger = logging.getLogger(__name__)


async def start_orders_checker():
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

    await connect_to_db(remove_data=False)
    logger.info("Orders checker has been started!")

    while True:
        await asyncio.sleep(10)

        last_user_id = 0
        user_data = None

        db_orders = await DbOrder(status=0).select()
        for order in db_orders:
            if order.tg_user_id != last_user_id:
                last_user_id = order.tg_user_id
                api_user = APIUser(telegram=last_user_id, balance=0, name="tguser", email="tg.user@gmail.com")
                user_data = await APIInterface.add_or_update_new_user(api_user=order)

            for task in user_data["data"]["tasks"]:
                task_id = task["id"]
