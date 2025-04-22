import logging

from aiogram import Router, F, types

from tg_bot.keyboards.inline import InlineMarkups as Im
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "how_to_start")
async def how_to_start_info(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {how_to_start_info.__name__}. user_id={uid}")

    text = [
        "ℹ️ Как начать работу?\n",
        "1. Нажмите “Заказать накрутку” в меню",
        "2. Выберите срок работы накрутки ПФ",
        "3. Выберите количество ПФ в день",
        "4. Укажите ссылку/ссылки на объявления через пробел или с новой строки",
        "5. Оплатите заказ",
        "6. Ожидайте выполнения!"
    ]
    markup = await Im.how_to_start()

    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)
