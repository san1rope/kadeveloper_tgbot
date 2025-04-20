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
        "<b>❇️ Активные заказы</b>\n",
        f"<b>Активных заказов: {len(db_orders)}</b>"
        "\n<b>⬇️ Для возвращения, используйте клавиатуру</b>"
    ]
    markup_main = await Im.back(callback_data="back_from_active_orders_menu")
    await Ut.send_step_message(user_id=uid, text="\n".join(text_main), markup=markup_main)

    for order in db_orders:
        text = [
            f"<b>Заказ #{order.id}</b>\n",
            f"<b>Количество дней: {order.period}</b>",
            f"<b>Количество ПФ: {order.pf}</b>",
            f"<b>Объявление: {order.advert_url}</b>",
            "\n<b>⬇️ Для дествия над заказом, используйте клавиатуру</b>"
        ]
        markup = await Im.order_actions(order_id=order.id)
        msg = await callback.message.answer(text="\n".join(text), reply_markup=markup)
        await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)


@router.callback_query(OrderActions.filter())
async def order_actions(callback: types.CallbackQuery, callback_data: OrderActions):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handled called. {order_actions.__name__}. user_id={uid}")

    if callback_data.action == "delete":
        text = [
            "<b>Вы действительно желаете удалить Ваш заказ?</b>"
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
            f"<b>Заказ #{order.id}</b>\n",
            f"<b>Количество дней: {order.period}</b>",
            f"<b>Количество ПФ: {order.pf}</b>",
            f"<b>Объявление: {order.advert_url}</b>",
            "\n<b>⬇️ Для дествия над заказом, используйте клавиатуру</b>"
        ]
        markup = await Im.order_actions(order_id=order.id)
        await callback.message.edit_text(text="\n".join(text), reply_markup=markup)

    elif callback_data.action == "delete":
        order = await DbOrder(db_id=callback_data.order_id).select()
        await DbOrder(db_id=callback_data.order_id).update(status=3)

        api_order = APIOrder(
            telegram=callback.from_user.username, link=order.advert_url, title="NULL",
            location="NULL", spend=0, limit=0
        )
        result = await APIInterface.add_or_update_new_task(api_order=api_order)
        print(f"result update task stop = {result}")

        text = [
            "<b>✅ Вы успешно удалили заказ!</b>"
        ]
        await callback.message.edit_text(text="\n".join(text))
