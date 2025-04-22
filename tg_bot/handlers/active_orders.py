import logging

from aiogram import Router, F, types

from tg_bot.db_models.quick_commands import DbOrder
from tg_bot.keyboards.inline import InlineMarkups as Im, OrderActions, OrderActConfirmation
from tg_bot.misc.api_interface import APIInterface
from tg_bot.misc.models import APIOrder
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "active_orders")
async def show_active_orders(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {show_active_orders.__name__}. user_id={uid}")

    db_orders = await DbOrder(tg_user_id=uid, status=0).select()

    text_main = [
        "❇️ Активные заказы\n",
        f"Активных заказов: {len(db_orders)}"
        "\n⬇️ Для возвращения, используйте клавиатуру"
    ]
    markup_main = await Im.back(callback_data="back_from_active_orders_menu")
    await Ut.send_step_message(user_id=uid, text="\n".join(text_main), markup=markup_main)

    for order in db_orders:
        text = [
            f"Заказ #{order.id}\n",
            f"Количество дней: {order.period}",
            f"Количество ПФ: {order.pf}",
            f"Объявление: {order.advert_url}",
            "\n⬇️ Для действия над заказом используйте клавиатуру."
        ]
        markup = await Im.order_actions(order_id=order.id)
        msg = await callback.message.answer(text="\n".join(text), reply_markup=markup, disable_web_page_preview=True)
        await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)


@router.callback_query(OrderActions.filter())
async def order_actions(callback: types.CallbackQuery, callback_data: OrderActions):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handled called. {order_actions.__name__}. user_id={uid}")

    if callback_data.action == "delete":
        text = [
            "Вы действительно желаете удалить Ваш заказ?"
        ]
        markup = await Im.order_confirmation(order_id=callback_data.order_id, action=callback_data.action)
        await callback.message.edit_text(text="\n".join(text), reply_markup=markup)


@router.callback_query(OrderActConfirmation.filter())
async def confirm_order_act(callback: types.CallbackQuery, callback_data: OrderActConfirmation):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handled called. {confirm_order_act.__name__}. user_id={uid}")

    if callback_data.action == "back":
        order = await DbOrder(db_id=callback_data.order_id).select()
        text = [
            f"Заказ #{order.id}\n",
            f"Количество дней: {order.period}",
            f"Количество ПФ: {order.pf}",
            f"Объявление: {order.advert_url}",
            "\n⬇️ Для действия над заказом используйте клавиатуру."
        ]
        markup = await Im.order_actions(order_id=order.id)
        await callback.message.edit_text(text="\n".join(text), reply_markup=markup)

    elif callback_data.action == "delete":
        text = [
            "Удаляю заказ..."
        ]
        await callback.message.edit_text(text="\n".join(text))

        order = await DbOrder(db_id=callback_data.order_id).select()

        api_order = APIOrder(
            telegram=uid, link=order.advert_url, title="title", category="cat1", location="location1", spend=0, limit=0)
        result = await APIInterface.add_or_update_new_task(api_order=api_order)
        if result["success"] is False:
            logger.error("Failed to update the task in the API!")

            text = [
                "🔴 Не удалось удалить заказ!\n",
                "Попробуйте позже, либо обратитесь в тех. поддержку!"
            ]

        else:
            await DbOrder(db_id=callback_data.order_id).update(status=3)
            text = [
                f"✅ Вы успешно удалили заказ #{callback_data.order_id}!"
            ]

        await callback.message.edit_text(text="\n".join(text))
