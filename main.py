import asyncio
import logging
from multiprocessing import Process

from aiogram.types import BotCommand

from config import Config
from tg_bot.db_models.db_gino import connect_to_db
from tg_bot.handlers import routers
from tg_bot.misc.orders_checker import start_orders_checker
from tg_bot.misc.startup import check_user_states
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)


async def main():
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

    await connect_to_db(remove_data=Config.DATABASE_CLEANUP)

    if routers:
        Config.DISPATCHER.include_routers(*routers)

    bot_commands = [
        BotCommand(command="start", description="Start menu"),
    ]
    await Config.BOT.set_my_commands(commands=bot_commands)
    await Config.BOT.delete_webhook(drop_pending_updates=True)

    Process(target=Ut.wrapper, args=(start_orders_checker,)).start()

    await check_user_states()
    await Config.DISPATCHER.start_polling(Config.BOT, allowed_updates=Config.DISPATCHER.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
