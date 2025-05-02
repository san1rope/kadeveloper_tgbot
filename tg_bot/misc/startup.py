from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from tg_bot.db_models.db_gino import connect_to_db
from tg_bot.db_models.quick_commands import TempOrder
from tg_bot.misc.states import CreateOrder


async def check_user_states():
    await connect_to_db(remove_data=False)

    temp_orders = await TempOrder().select()
    for t_order in temp_orders:
        t_order: TempOrder

        new_key = StorageKey(user_id=t_order.tg_user_id, chat_id=t_order.chat_id, bot_id=Config.BOT.id)
        new_state = FSMContext(storage=MemoryStorage(), key=new_key)

        state_to_set = getattr(CreateOrder, t_order.current_state)
        await new_state.set_state(state_to_set)
