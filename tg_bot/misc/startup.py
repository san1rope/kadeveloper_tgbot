import logging

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from tg_bot.db_models.db_gino import connect_to_db
from tg_bot.db_models.quick_commands import DbTempOrder, TempOrder
from tg_bot.misc.states import CreateOrder

logger = logging.getLogger(__name__)


async def check_user_states():
    await connect_to_db(remove_data=False)
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

    temp_orders = await DbTempOrder().select()
    for t_order in temp_orders:
        t_order: TempOrder

        new_key = StorageKey(user_id=t_order.tg_user_id, chat_id=t_order.tg_user_id, bot_id=Config.BOT.id)
        new_state = FSMContext(storage=MemoryStorage(), key=new_key)

        state_to_set = getattr(CreateOrder, t_order.current_state)
        print(f"state_to_set = {state_to_set}")
        await new_state.set_state(state_to_set)
        logging.info(f"Установил состояние для {t_order.tg_user_id}")
