import logging
from typing import Union

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiohttp import ClientSession

from config import Config
from tg_bot.db_models.quick_commands import DbUser
from tg_bot.handlers.start import cmd_start
from tg_bot.keyboards.inline import InlineMarkups as Im
from tg_bot.misc.api_interface import APIInterface
from tg_bot.misc.models import APIUser
from tg_bot.misc.states import CreateOrder
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "order_feedbacks")
async def choose_period(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {choose_period.__name__}. user_id={uid}")

    text = [
        "<b>📄 Создание ордера</b>\n",
        "<b>Выберите время работы накрутки:</b>",
        "\n<b>⬇️ Используйте клавиатуру ниже</b>"
    ]
    markup = await Im.order_period()
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)

    await state.set_state(CreateOrder.ChoosePeriod)


@router.callback_query(CreateOrder.ChoosePeriod)
@router.message(CreateOrder.ChoosePeriod)
async def choose_pf_quantity(message: [types.CallbackQuery, types.Message], state: FSMContext,
                             from_back_btn: bool = False):
    uid = message.from_user.id
    logger.info(f"Handler called. {choose_pf_quantity.__name__}. user_id={uid}")

    data = await state.get_data()

    if isinstance(message, types.CallbackQuery):
        await message.answer()
        cd = message.data

        if cd == "cancel":
            return await cmd_start(message=message)

        elif cd == "write_quantity":
            text = [
                "<b>📄 Создание ордера</b>\n",
                "<b>✍️ Введите нужное количество дней</b>"
            ]
            markup = await Im.back(callback_data="back_from_input")

            return await Ut.send_step_message(user_id=uid, text='\n'.join(text), markup=markup)

        elif cd == "back_from_input" and not from_back_btn:
            return await choose_period(callback=message, state=state)

        else:
            if not from_back_btn:
                selected_period = int(cd)
                await state.update_data(period=selected_period)

            else:
                selected_period = data.get("period")

    elif isinstance(message, types.Message):
        input_text = message.text.strip()
        if not input_text.isdigit():
            text = "<b>🔴 Вы ввели количество в неверном формате! Нужно писать только целые числа!</b>"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        input_text = int(input_text)
        if input_text <= 0:
            text = "<b>🔴 Количество не может быть меньше либо равно нулю!</b>"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        selected_period = input_text
        await state.update_data(period=selected_period)

    else:
        return

    text = [
        "<b>📄 Создание ордера</b>\n",
        f"<b>Вы выбрали дней: {selected_period}</b>\n"
        "<b>Выберите / Введите необходимое количество поведенческого фактора на день</b>",
        "\n<b>🚀 50 ПФ - частый выбор наших клиентов!</b>",
        "<b>💴 Цена 4 рубля за 1 ПФ</b>"
        "\n<b>⬇️ Используйте клавиатуру ниже</b>"
    ]
    markup = await Im.order_pf()
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)

    await state.set_state(CreateOrder.ChoosePFQuantity)


@router.callback_query(CreateOrder.ChoosePFQuantity)
@router.message(CreateOrder.ChoosePFQuantity)
async def write_advert_url(message: Union[types.CallbackQuery, types.Message], state: FSMContext,
                           from_back_btn: bool = False):
    uid = message.from_user.id
    logger.info(f"Handler called. {write_advert_url.__name__}. user_id={uid}")

    if isinstance(message, types.CallbackQuery):
        await message.answer()
        cd = message.data

        if cd == "back" and not from_back_btn:
            return await choose_period(callback=message, state=state)

        elif cd == "write_quantity":
            text = [
                "<b>📄 Создание ордера</b>\n",
                "<b>✍️ Введите нужное количество ПФ</b>"
            ]
            markup = await Im.back(callback_data="back_from_input")

            return await Ut.send_step_message(user_id=uid, text='\n'.join(text), markup=markup)

        elif cd == "back_from_input":
            return await choose_pf_quantity(message=message, state=state, from_back_btn=True)

        else:
            if not from_back_btn:
                selected_pf = int(cd)
                await state.update_data(pf=selected_pf)

            else:
                data = await state.get_data()
                selected_pf = data.get("pf")

    elif isinstance(message, types.Message):
        input_text = message.text.strip()
        if not input_text.isdigit():
            text = "<b>🔴 Вы ввели количество в неверном формате! Нужно писать только целые числа!</b>"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        input_text = int(input_text)
        if input_text <= 0:
            text = "<b>🔴 Количество не может быть меньше либо равно нулю!</b>"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        selected_pf = input_text
        await state.update_data(pf=selected_pf)

    else:
        return

    text = [
        "<b>📄 Создание ордера</b>\n",
        f"<b>Вы выбрали количество ПФ: {selected_pf}</b>\n",
        "<b>✍️ Вставьте ссылку на объявление или на несколько объявлений через пробел или перенос строки (Ctrl + Enter)</b>"
    ]
    markup = await Im.back(callback_data="back")
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)

    await state.set_state(CreateOrder.InsertAdvertsUrls)


@router.message(CreateOrder.InsertAdvertsUrls)
@router.callback_query(CreateOrder.InsertAdvertsUrls)
async def make_payment(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    uid = message.from_user.id
    logger.info(f"Handler called. {make_payment.__name__}. user_id={uid}")

    if isinstance(message, types.CallbackQuery):
        await message.answer()
        cd = message.data

        if cd == "back":
            return await choose_pf_quantity(message=message, state=state, from_back_btn=True)

        else:
            return

    elif isinstance(message, types.Message):
        input_text = message.text.strip()
        if not input_text.startswith("https://"):
            text = "<b>🔴 Вы ввели неверные данные! Нужно вставлять ссылки на объявления!\nЧто-бы вставить 2 и больше ссылок, нужно использовать перенос строки (Ctrl + Enter)</b>"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        adverts_urls = input_text.split("\n")
        adverts_urls = [i.split() for i in adverts_urls]
        await state.update_data(adverts_urls=adverts_urls)

    else:
        return

    text_urls = ""
    for i in adverts_urls:
        text_urls += f"\n{i}"

    data = await state.get_data()
    price = data["pf"] * 4

    text = [
        "<b>📄 Создание ордера</b>\n",
        f"<b>Введенные вами ссылки:{text_urls}</b>\n",
        "<b>💴 Теперь вам нужно оплатить задачу!</b>"
        f"<b>Для оплаты задачи сделайте перевод на сумму {price} рублей</b>",
        f"<b>⬇️ После оплаты используйте клавиатуру ниже</b>"
    ]
    markup = await Im.payment()
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)

    await state.set_state(CreateOrder.MakePayment)


@router.callback_query(CreateOrder.MakePayment)
async def create_process_has_completed(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {create_process_has_completed.__name__}. user_id={uid}")

    cd = callback.data
    if cd == "back":
        return await write_advert_url(message=callback, state=state, from_back_btn=True)

    elif cd == "payment_completed":
        data = await state.get_data()
        period = data["period"]
        pf = data["pf"]
        adverts_urls = data["adverts_urls"]

        db_user = await DbUser(tg_user_id=uid).select()
        if not db_user:
            db_user = await DbUser(tg_user_id=uid, balance=0).add()

            api_user = APIUser(telegram=callback.from_user.username, balance=0)
            result = await APIInterface.add_new_user(api_user=api_user)
            if result["success"] is False:
                logger.error("Не удалось добавить нового юзера в API!")

        text = [
            "<b>✅ Заказ создан!</b>\n",
            "<b>ℹ️ Вы можете следить за статусом выполнения в меню Активные заказы.</b>\n",
            "<b>ℹ️ После подтверждения оплаты просмотры будут начаты и вы получите уведомление.</b>",
            "\n<b>⬇️ Используйте клавиатуру ниже</b>"
        ]
        markup = await Im.order_created()
        await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)
