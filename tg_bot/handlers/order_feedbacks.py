import json
import logging
from typing import Union

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from tg_bot.db_models.quick_commands import DbPayment
from tg_bot.handlers.start import cmd_start
from tg_bot.keyboards.inline import InlineMarkups as Im
from tg_bot.misc.api_interface import APIInterface
from tg_bot.misc.models import APIUser
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
        "📄 Создание ордера\n",
        "Выберите время работы накрутки:",
        "\n⬇️ Используйте клавиатуру ниже"
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
                "📄 Создание ордера\n",
                "✍️ Введите нужное количество дней"
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
            text = "🔴 Вы ввели количество в неверном формате! Нужно писать только целые числа!"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        input_text = int(input_text)
        if input_text <= 0:
            text = "🔴 Количество не может быть меньше либо равно нулю!"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        if input_text > 90:
            text = "🔴 Максимальное количество: 90"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        selected_period = input_text
        await state.update_data(period=selected_period)

    else:
        return

    text = [
        "📄 Создание ордера\n",
        f"Вы выбрали дней: {selected_period}\n"
        "Выберите / Введите необходимое количество поведенческого фактора на день",
        "\n🚀 50 ПФ - частый выбор наших клиентов!",
        "💴 Цена 4 рубля за 1 ПФ"
        "\n⬇️ Используйте клавиатуру ниже"
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
                "📄 Создание ордера\n",
                "✍️ Введите нужное количество ПФ"
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
            text = "🔴 Вы ввели количество в неверном формате! Нужно писать только целые числа!"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        input_text = int(input_text)
        if input_text <= 0:
            text = "🔴 Количество не может быть меньше либо равно нулю!"
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        selected_pf = input_text
        await state.update_data(pf=selected_pf)

    else:
        return

    text = [
        "📄 Создание ордера\n",
        f"Вы выбрали количество ПФ: {selected_pf}\n",
        "✍️ Вставьте ссылку на объявление или на несколько объявлений через пробел или перенос строки (Ctrl + Enter)"
    ]
    markup = await Im.back(callback_data="back")
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)

    await state.set_state(CreateOrder.InsertAdvertsUrls)


@router.message(CreateOrder.InsertAdvertsUrls)
@router.callback_query(CreateOrder.InsertAdvertsUrls)
async def make_payment(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    uid = message.from_user.id
    logger.info(f"Handler called. {make_payment.__name__}. user_id={uid}")

    data = await state.get_data()

    if isinstance(message, types.CallbackQuery):
        await message.answer()
        cd = message.data

        if cd == "back":
            return await choose_pf_quantity(message=message, state=state, from_back_btn=True)

        else:
            return

    elif isinstance(message, types.Message):
        input_text = message.text.strip()
        print(f"input_text = {input_text}")

        api_user = APIUser(telegram=uid, name="tguser", email="tg.user@gmail.com")
        userdata = await APIInterface.add_or_update_new_user(api_user=api_user)
        tasks = userdata["data"]["tasks"]
        tasks_links = [t["link"] for t in tasks]

        is_exist_texts = []
        adverts_urls = []
        wrong_urls = []
        for input_url in input_text.split("\n"):
            input_url = input_url.strip()

            urls_list = input_url.split(" ")
            if len(urls_list) > 1:
                for url_sec in urls_list:
                    if await Ut.verify_advertisement_url(url=url_sec):
                        if url_sec not in adverts_urls:
                            if "?" in url_sec:
                                url_sec = url_sec[:url_sec.rfind("?")]

                            if url_sec in tasks_links:
                                text = [
                                    "🔴 Уже есть активная задача с этим объявлением!\n",
                                    "Вы не можете создать 2 задачи на 1 объявление!"
                                ]
                                is_exist_texts.append(text)
                                continue

                            adv_name, adv_category, adv_location = await Ut.parse_advertisement(url=url_sec)
                            if adv_name is None:
                                text = [
                                    f"🔴 Не удалось получить данные о {url_sec}\n",
                                    "Убедитесь, что ссылка введена верно и объявление доступное!",
                                    "\nВ ином случае попробуйте позже, либо обратитесь в поддержку!"
                                ]
                                msg = await message.answer(text="\n".join(text), disable_web_page_preview=True)
                                await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)
                                continue

                            adverts_urls.append({
                                "url": url_sec, "title": adv_name, "category": adv_category, "location": adv_location,
                                "period": data["period"], "pf": data["pf"]
                            })

                    else:
                        if url_sec not in wrong_urls:
                            wrong_urls.append(url_sec)

            else:
                if await Ut.verify_advertisement_url(url=input_url):
                    if input_url not in adverts_urls:
                        if "?" in input_url:
                            input_url = input_url[:input_url.rfind("?")]

                        if input_url in tasks_links:
                            text = [
                                "🔴 Уже есть активная задача с объявлением!\n",
                                f"Ссылка: {input_url}\n"
                                "Вы не можете создать 2 задачи на 1 объявление!"
                            ]
                            msg = await message.answer(text="\n".join(text), disable_web_page_preview=True)
                            await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)
                            return

                        adv_name, adv_category, adv_location = await Ut.parse_advertisement(url=input_url)
                        if adv_name is None:
                            text = [
                                f"🔴 Не удалось получить данные о {input_url}\n",
                                "Убедитесь, что ссылка введена верно и объявление доступное!",
                                "\nВ ином случае попробуйте позже, либо обратитесь в поддержку!"
                            ]
                            msg = await message.answer(text="\n".join(text), disable_web_page_preview=True)
                            await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)
                            return

                        adverts_urls.append({
                            "url": input_url, "title": adv_name, "category": adv_category, "location": adv_location,
                            "period": data["period"], "pf": data["pf"]
                        })

                else:
                    if input_url not in wrong_urls:
                        wrong_urls.append(input_url)

        await state.update_data(adverts_urls=adverts_urls)

    else:
        return

    data = await state.get_data()
    price = (data["pf"] * data["period"]) * len(adverts_urls)

    if adverts_urls:
        text = [
            "📄 Создание ордера\n",
            f"🖊 Введенные вами ссылки:",
        ]

        for adv_data in adverts_urls:
            print(f"adv_data = {adv_data}")
            text.append(f"{adverts_urls.index(adv_data) + 1}. {adv_data['url']}")

        text.extend([
            "\n💴 Теперь вам нужно оплатить задачу!"
            f"Для оплаты задачи сделайте перевод на сумму {price} рублей по номеру +7 (904) 084-44-92 (Альфабанк, Артём К)",
            f"\n⬇️ После оплаты нажмите кнопку Оплачено"
        ])

        if wrong_urls:
            text_wrong_urls = [
                "🔴 Остальные ссылки были не распознаны!",
                "💭 Ссылка должна начинаться на https://avito.ru/",
                "\nℹ️ Чтобы вставить 2 и более ссылки, используйте перенос строки (Ctrl + Enter) или пробел (Space)\n"
            ]
            text.insert(2, "\n".join(text_wrong_urls))

    else:
        text = [
            "🔴 Ссылки не распознаны!\n",
            "💭 Ссылка должна начинаться на https://avito.ru/",
            "\nℹ️ Чтобы вставить 2 и более ссылки, используйте перенос строки (Ctrl + Enter) или пробел (Space)"
        ]
        msg = await message.answer(text="\n".join(text), disable_web_page_preview=True)
        return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

    markup = await Im.payment()
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)
    for ex_text in is_exist_texts:
        msg = await message.answer(text="\n".join(ex_text), disable_web_page_preview=True)
        await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

    await state.update_data(price=price)
    await state.set_state(CreateOrder.MakePayment)


@router.callback_query(CreateOrder.MakePayment)
async def payment_confirmation(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {payment_confirmation.__name__}. user_id={uid}")

    cd = callback.data
    if cd == "back":
        return await write_advert_url(message=callback, state=state, from_back_btn=True)

    elif cd == "payment_completed":
        data = await state.get_data()

        payment_data = {"data": data["adverts_urls"]}
        payment = await DbPayment(tg_user_id=uid, confirmation=0, data=json.dumps(payment_data)).add()
        if payment:
            text = [
                "✅ Ваша заявка была отправлена администратору!\n",
                "ℹ️ После того, как админ подтвердит вашу оплату, ваш заказ будет переведен в работу!",
                "\n⬇️ Используйте клавиатуру ниже"
            ]
            markup = await Im.order_created()
            await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)
            await state.clear()

            await Ut.send_payment_confirmation_to_admins(payment=payment, price=data["price"])

        else:
            text = [
                "🔴 Не удалось отправить заявку администратору!\n",
                "Попробуйте ещё раз, либо обратитесь к администратору!"
            ]
            msg = await callback.message.answer(text="\n".join(text), disable_web_page_preview=True)
            await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)
