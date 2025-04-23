import asyncio
import logging

from config import Config
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
                api_user = APIUser(telegram=last_user_id, name="tguser", email="tg.user@gmail.com")
                user_data = await APIInterface.add_or_update_new_user(api_user=api_user)
                if user_data["success"] is False:
                    logger.error("Не удалось получить данные о пользователе!")
                    continue

            for task in user_data["data"]["tasks"]:
                if task["id"] == order.api_id and task["views"] == task["spend"]:
                    await DbOrder(db_id=order.id).update(status=1)
                    text = [
                        f"✅ Задание #{order.id} выполнено!",
                        f"\nОбъявление: {order.advert_url}",
                    ]

                    await Config.BOT.send_message(chat_id=order.tg_chat_id, text="\n".join(text))

                    for admin_id in Config.ADMINS:
                        await Config.BOT.send_message(chat_id=admin_id, text="\n".join(text))
