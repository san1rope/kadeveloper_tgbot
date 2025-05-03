import logging
from typing import Union

from aiogram import Router, F, types, enums
from aiogram.filters import CommandStart

from tg_bot.db_models.quick_commands import DbOrder
from tg_bot.keyboards.inline import InlineMarkups as Im
from tg_bot.misc.api_interface import APIInterface
from tg_bot.misc.models import APIUser
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type == enums.ChatType.PRIVATE, CommandStart())
@router.callback_query(F.data == "back_from_order")
@router.callback_query(F.data == "back_from_how_to_start")
@router.callback_query(F.data == "back_from_questions_menu")
@router.callback_query(F.data == "back_from_active_orders_menu")
async def cmd_start(message: Union[types.Message, types.CallbackQuery]):
    uid = message.from_user.id
    logger.info(f"Handler called. {cmd_start.__name__}. user_id={uid}")

    if isinstance(message, types.CallbackQuery):
        await message.answer()
        message = message.message

    text = [
        "Получаю данные о пользователе..."
    ]
    msg = await Ut.send_step_message(user_id=uid, text="\n".join(text))

    api_user = APIUser(telegram=uid, name="tguser", email="tg.user@gmail.com")
    result = await APIInterface.add_or_update_new_user(api_user=api_user)
    balance = int(result['data']['user']['balance'])

    username = message.from_user.username

    currency_text = "рубл"
    ods = balance % 10
    if ods == 1:
        currency_text += "ь"

    elif ods in [2, 3, 4]:
        currency_text += "я"

    else:
        currency_text += "ей"

    text = [
        f"👋 Приветствую{f', {username}' if username else ''}! Баланс {balance} рублей.\n",
        """🚀Взлетайте в ТОП и рекомендации Авито с нашим ботом!

Забудьте о низком рейтинге! Наш бот для накрутки ОРГАНИЧЕСКИХ поведенческих факторов (ПФ) - это ваш ключ к привлечению большего количества клиентов! ПФ (поиск в выдаче, просмотры, добавления в избранное, контакты) сигнализируют алгоритму Авито о высокой востребованности вашего объявления, что автоматически повышает его позицию в результатах поиска. Чем больше ПФ, тем выше ваше объявление в выдаче и тем больше людей его увидят! 🤩

Почему нас выбирают?

* Супер безопасно! Для накрутки используются только настоящие активные аккаунты Авито, никаких фейковых аккаунтов
* Самая низкая в России! 4 рубля за 1 поведенческий фактор
* Качественные ПФ! Случайное выполнение нескольких действий, имитирующих действия пользователя - просмотр фото, описания, карты, телефона и т.п.
* Никаких ложных срабатываний и недокруток! Если просмотр не выполнен, он не будет засчитан и по окончанию задачи останется на балансе.
* Круглосуточная работа! Наш бот работает 24/7, не пропускайте ни одной возможности продвинуть объявления! 

🔥Закажите накрутку ПФ прямо сейчас и наблюдайте, как ваши объявления поднимаются в ТОП!
        """
    ]

    active_orders = await DbOrder(tg_user_id=uid, status=0).select()
    markup = await Im.start_menu(how_to_start_btn=not bool(active_orders))
    await msg.edit_text(text="\n".join(text), reply_markup=markup)
