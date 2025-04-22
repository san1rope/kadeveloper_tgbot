import logging
from typing import Union

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from tg_bot.db_models.quick_commands import DbUser, DbOrder
from tg_bot.handlers.start import cmd_start
from tg_bot.keyboards.inline import InlineMarkups as Im
from tg_bot.misc.api_interface import APIInterface
from tg_bot.misc.models import APIUser, APIOrder
from tg_bot.misc.states import CreateOrder
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "continue_create_order")
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
            await state.clear()
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
        # if not input_text.startswith("https://"):
        #     text = "<b>🔴 Вы ввели неверные данные! Нужно вставлять ссылки на объявления!\nЧто-бы вставить 2 и больше ссылок, нужно использовать перенос строки (Ctrl + Enter)</b>"
        #     msg = await message.answer(text=text)
        #     return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        adverts_urls = []
        wrong_urls = []
        for input_url in input_text.split("\n"):
            input_url = input_url.strip()
            if input_url in adverts_urls or input_url in wrong_urls:
                continue

            if (not input_url.startswith("https://www.avito.ru/")) or ("?" in input_url):
                wrong_urls.append(input_url)
                continue

            adverts_urls.append(input_url.strip())

        await state.update_data(adverts_urls=adverts_urls)

    else:
        return

    data = await state.get_data()
    price = (data["pf"] * data["period"]) * len(adverts_urls)

    if adverts_urls:
        text_urls = '\n'.join(adverts_urls)
        text = [
            "<b>📄 Создание ордера</b>\n",
            f"<b>Введенные вами ссылки:\n{text_urls}</b>\n",
            "<b>💴 Теперь вам нужно оплатить задачу!</b>"
            f"<b>Для оплаты задачи сделайте перевод на сумму {price} рублей</b>",
            f"\n<b>⬇️ После оплаты используйте клавиатуру ниже</b>"
        ]
        if wrong_urls:
            text_wrong_urls = [
                "<b>Остальные ссылки были введены в неверном формате!</b>",
                "<b>Ссылка должна начинаться на https://avito.ru/ и не должна иметь параметров (?, &)</b>",
                "<b>\nЧто-бы вставить 2 и больше ссылок, нужно использовать перенос строки (Ctrl + Enter)</b>\n"
            ]
            text.insert(2, "\n".join(text_wrong_urls))

    else:
        text = [
            "<b>🔴 Вы вставили ссылки в неверном формате!</b>\n",
            "<b>Ссылка должна начинаться на https://avito.ru/ и не должна иметь параметров (?, &)</b>",
            "<b>\nЧто-бы вставить 2 и больше ссылок, нужно использовать перенос строки (Ctrl + Enter)</b>"
        ]
        msg = await message.answer(text="\n".join(text))
        return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

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
        text = [
            "<b>Создаю заказ...</b>"
        ]
        await Ut.send_step_message(user_id=uid, text="\n".join(text))

        db_user = await DbUser(tg_user_id=uid).select()
        if not db_user:
            await DbUser(tg_user_id=uid, balance=0).add()
            api_user = APIUser(telegram=uid, balance=0, name="tguser", email="tg.user@gmail.com")
            result = await APIInterface.add_or_update_new_user(api_user=api_user)
            if result["success"] is False:
                logger.error("Failed to add/update new user in API!")

                text = [
                    "<b>🔴 Не удалось добавить Вас в систему!</b>",
                    "<b>Попробуйте ещё раз, либо обратитесь в поддержку!</b>"
                ]
                markup = await Im.back(callback_data="back_from_order")
                await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)

                return await state.clear()

        data = await state.get_data()
        period = data["period"]
        pf = data["pf"]
        adverts_urls = data["adverts_urls"]

        successful_created = 0
        for adv_url in adverts_urls:
            adv_name, adv_category, adv_location = await Ut.parse_advertisement(url=adv_url)
            api_order = APIOrder(
                telegram=uid, link=adv_url, title=adv_name, spend=pf * period, limit=pf, category=adv_category,
                location=adv_location)
            result = await APIInterface.add_or_update_new_task(api_order=api_order)
            if result["success"] is False:
                logger.error("Failed to add/update task in API!")

                text = [
                    f"<b>🔴 Не удалось создать заказ по {adv_url}</b>\n",
                    "<b>Убедитесь, что у вас нету активных заказов с этим объявлением</b>",
                    "<b>\nВ ином случае попробуйте позже, либо обратитесь в поддержку!</b>"
                ]

            else:
                api_id = -1
                for task in result["data"]["tasks"]:
                    if task["link"] == adv_url:
                        api_id = int(task["id"])
                        break

                await DbOrder(tg_user_id=uid, api_id=api_id, status=0, period=data["period"], pf=data["pf"],
                              advert_url=adv_url).add()
                successful_created += 1
                text = [
                    "<b>✅ Заказ создан!</b>\n",
                    f"<b>Объявление: {adv_url}</b>",
                ]

            msg = await callback.message.answer(text="\n".join(text))
            await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        if successful_created == len(adverts_urls):
            text = [
                "<b>✅ Все заказы были созданы!</b>\n",
                "<b>ℹ️ Вы можете следить за статусом выполнения в меню Активные заказы.</b>\n",
                "<b>ℹ️ После подтверждения оплаты просмотры будут начаты и вы получите уведомление.</b>",
                "\n<b>⬇️ Используйте клавиатуру ниже</b>"
            ]

        elif successful_created and successful_created < len(adverts_urls):
            text = [
                "<b>ℹ️ Процесс создания заказов завершен!</b>\n",
                "<b>Некоторые заказы не удалось создать!</b>",
                "<b>Убедитесь, что вы не вставляли ссылки на объявления уже активных заказов</b>\n",
                "<b>ℹ️ Вы можете следить за статусом выполнения в меню Активные заказы.</b>\n",
                "<b>ℹ️ После подтверждения оплаты просмотры будут начаты и вы получите уведомление.</b>",
                "\n<b>⬇️ Используйте клавиатуру ниже</b>"
            ]

        elif not successful_created:
            text = [
                "<b>🔴 Не удалось создать ни единого заказа!</b>",
                "<b>Убедитесь, что вы не вставляли ссылки на объявления уже активных заказов, либо попробуйте позже</b>",
                "\n<b>⬇️ Используйте клавиатуру ниже</b>"
            ]

        markup = await Im.order_created()
        msg = await callback.message.answer(text="\n".join(text), reply_markup=markup)
        await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        await state.clear()
