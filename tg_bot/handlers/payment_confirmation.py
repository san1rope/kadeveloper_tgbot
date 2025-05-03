import json
import logging

from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest

from config import Config
from tg_bot.db_models.quick_commands import DbPayment, DbOrder
from tg_bot.db_models.schemas import Payment
from tg_bot.keyboards.inline import PaymentConfirmation, InlineMarkups as Im
from tg_bot.misc.api_interface import APIInterface
from tg_bot.misc.models import APIOrder, APIUser
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(PaymentConfirmation.filter())
async def confirm_payment(callback: types.CallbackQuery, callback_data: PaymentConfirmation):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {confirm_payment.__name__}. user_id={uid}")

    payment: Payment = await DbPayment(db_id=callback_data.payment_id).select()

    try:
        username = (await Config.BOT.get_chat(chat_id=payment.tg_user_id)).username

    except TelegramBadRequest:
        username = "Не удалось получить"

    if callback_data.confirm:
        text = [
            "✅ Платеж успешно подтвержден! Создаю заказ..."
        ]
        await DbPayment(db_id=payment.id).update(confirmation=1)
        await callback.message.edit_text(text="Создаю заказ...")

        order_data = json.loads(payment.data)
        for ad in order_data["data"]:
            ad = json.loads(ad)

            api_order = APIOrder(
                telegram=uid, link=ad["url"], title=ad["title"], spend=ad["pf"] * ad["period"], limit=ad["pf"],
                category=ad["category"], location=ad["location"]
            )
            result = await APIInterface.add_or_update_new_task(api_order=api_order)
            if result["success"] is False:
                logger.error("Failed to add/update task in API!")
                text_error = [
                    "🔴 Не удалось создать заказ!\n",
                    f"Пользователь: @{username}"
                    f"Ссылка: {ad['url']}",
                    f"\nОтвет сервера: {str(result)}"
                ]
                return await callback.message.answer(text="\n".join(text_error), disable_web_page_preview=True)

            else:
                api_id = -1
                for task in result["data"]["tasks"]:
                    if task["link"] == ad['url']:
                        api_id = int(task["id"])
                        break

                db_order = await DbOrder(tg_user_id=uid, api_id=api_id, status=0, period=ad["period"], pf=ad["pf"],
                                         advert_url=ad['url']).add()

                text_for_user = [
                    "✅ Платеж подтвежден!\n"
                    f"Баланс пополнен на {payment.price} рублей. Задача #{db_order.id} запущена.\n",
                    "⬇️ Используйте клавиатуру ниже"
                ]
                markup = await Im.payment_confirmed()

                api_user = APIUser(telegram=payment.tg_user_id, name="tguser", email="tg.user@gmail.com")
                result = await APIInterface.add_or_update_new_user(api_user=api_user)
                if result["success"] is False:
                    text_error = [
                        "🔴 Не удалось получить баланс юзера!\n",
                        f"Пользователь: @{username}",
                        f"Ссылка: {ad['url']}",
                        f"\nОтвет сервера: {str(result)}"
                    ]
                    return await callback.message.answer(text="\n".join(text_error), disable_web_page_preview=True)

                api_user.balance = int(result["data"]["user"]["balance"]) + payment.price
                result = await APIInterface.add_or_update_new_user(api_user=api_user)
                if result["success"] is False:
                    text_error = [
                        "🔴 Не удалось обновить баланс юзера!\n",
                        f"Пользователь: @{username}",
                        f"Ссылка: {ad['url']}",
                        f"\nОтвет сервера: {str(result)}"
                    ]
                    return await callback.message.answer(text="\n".join(text_error), disable_web_page_preview=True)
    else:
        text = [
            "🔘 Вы отменили платеж!"
        ]
        await DbPayment(db_id=payment.id).update(confirmation=2)

        text_for_user = [
            "🔴 Админ указал, что платежа не было!\n",
            "Ваш заказ отменен."
        ]
        markup = None

    await callback.message.edit_text(text="\n".join(text))

    try:
        msg = await Config.BOT.send_message(chat_id=payment.tg_user_id, text="\n".join(text_for_user),
                                            reply_markup=markup, disable_web_page_preview=True)
        await Ut.add_msg_to_delete(user_id=payment.tg_user_id, msg_id=msg.message_id)

    except TelegramBadRequest:
        pass
