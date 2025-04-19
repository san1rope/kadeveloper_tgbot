import logging

from aiogram import Router, F, types

from tg_bot.db_models.quick_commands import DbOrder

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "active_orders")
async def show_active_orders(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {show_active_orders.__name__}. user_id={uid}")

    db_orders = await DbOrder(tg_user_id=uid).select()
