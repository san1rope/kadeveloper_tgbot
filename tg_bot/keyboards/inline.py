from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config


class CommonQuestions(CallbackData, prefix="cq"):
    question_id: int


class OrderActions(CallbackData, prefix="oa"):
    action: str
    order_id: int


class OrderActConfirmation(CallbackData, prefix="oac"):
    action: str
    order_id: int


class InlineMarkups:
    __btn_text_active_orders = "❇️ Активные заказы"
    __btn_text_back = "⬅️ Назад"
    __btn_text_order_feedbacks = "📄 Заказать накрутку"
    __btn_text_enter_required_quantity = "✍️ Ввести нужное количество"
    __btn_text_cancel = "🔘 Отменить"
    __btn_text_continue = "➡️ Продолжить"

    @classmethod
    async def start_menu(cls, how_to_start_btn: bool = False) -> InlineKeyboardMarkup:
        if how_to_start_btn:
            changeable_btn = InlineKeyboardButton(text="ℹ️ Как начать работу", callback_data="how_to_start")

        else:
            changeable_btn = InlineKeyboardButton(text=cls.__btn_text_active_orders, callback_data="active_orders")

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    changeable_btn
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_order_feedbacks, callback_data="order_feedbacks")
                ],
                [
                    InlineKeyboardButton(text="📰 Новости платформы", url=Config.TELEGRAM_CHANNEL),
                    InlineKeyboardButton(text="❔ Есть вопрос", callback_data="ask_question")
                ]
            ]
        )

    @classmethod
    async def how_to_start(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=cls.__btn_text_order_feedbacks, callback_data="order_feedbacks")
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_back, callback_data="back_from_how_to_start")
                ]
            ]
        )

    @classmethod
    async def order_period(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="День", callback_data="1"),
                    InlineKeyboardButton(text="Неделя", callback_data="7"),
                    InlineKeyboardButton(text="Месяц", callback_data="30")
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_enter_required_quantity, callback_data="write_quantity")
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_cancel, callback_data="cancel")
                ]
            ]
        )

    @classmethod
    async def order_pf(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="5", callback_data="5"),
                    InlineKeyboardButton(text="10", callback_data="10"),
                    InlineKeyboardButton(text="20", callback_data="20"),
                    InlineKeyboardButton(text="30", callback_data="30"),
                    InlineKeyboardButton(text="50", callback_data="50")
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_enter_required_quantity, callback_data="write_quantity")
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_back, callback_data="back")
                ]
            ]
        )

    @classmethod
    async def payment(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💴 Оплачено", callback_data="payment_completed")
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_back, callback_data="back")
                ]
            ]
        )

    @classmethod
    async def order_created(cls):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=cls.__btn_text_active_orders, callback_data="active_orders")
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_continue, callback_data="continue_create_order")
                ]
            ]
        )

    @classmethod
    async def back(cls, callback_data: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=cls.__btn_text_back, callback_data=callback_data)
                ]
            ]
        )

    @classmethod
    async def common_questions(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Как работает накрутка ПФ",
                                         callback_data=CommonQuestions(question_id=1).pack())
                ],
                [
                    InlineKeyboardButton(text="Лучшая методика накрутки",
                                         callback_data=CommonQuestions(question_id=2).pack())
                ],
                [
                    InlineKeyboardButton(text="ПФ на объявления в аккаунте одним днём",
                                         callback_data=CommonQuestions(question_id=3).pack())
                ],
                [
                    InlineKeyboardButton(text="Задать вопрос", url=Config.SUPPORT_TELEGRAM_URL)
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_back, callback_data="back_from_questions_menu")
                ]
            ]
        )

    @classmethod
    async def order_actions(cls, order_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Удалить",
                                         callback_data=OrderActions(order_id=order_id, action="delete").pack())
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_back,
                                         callback_data="back_from_questions_menu")
                ]
            ]
        )

    @classmethod
    async def order_confirmation(cls, order_id: int, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Подтвердить",
                                         callback_data=OrderActConfirmation(action=action, order_id=order_id).pack())
                ],
                [
                    InlineKeyboardButton(text=cls.__btn_text_back,
                                         callback_data=OrderActConfirmation(action="back", order_id=order_id).pack())
                ]
            ]
        )
