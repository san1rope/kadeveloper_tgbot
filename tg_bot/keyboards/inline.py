from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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
                    InlineKeyboardButton(text="Новости платформы", callback_data="platform_news"),
                    InlineKeyboardButton(text="Есть вопрос", callback_data="ask_question")
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
                    InlineKeyboardButton(text="💴 Оплатил", callback_data="payment_completed")
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
