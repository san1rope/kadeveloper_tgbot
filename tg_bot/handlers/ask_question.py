import logging

from aiogram import Router, F, types

from tg_bot.keyboards.inline import InlineMarkups as Im, CommonQuestions
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "ask_question")
@router.callback_query(F.data == "back_from_question_answer")
async def show_common_questions(callback: types.CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {show_common_questions.__name__}. user_id={uid}")

    text = [
        "❔ Частые вопросы\n",
        "Здесь собраны очень часто задаваемые вопросы",
        "Если вы не нашли ответ на свой вопрос, выбирайте кнопку - Задать вопрос"
        "\n⬇️ Используйте клавиатуру ниже"
    ]
    markup = await Im.common_questions()
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)


@router.callback_query(CommonQuestions.filter())
async def question_1(callback: types.CallbackQuery, callback_data: CommonQuestions):
    await callback.answer()
    uid = callback.from_user.id
    logger.info(f"Handler called. {question_1.__name__}. user_id={uid}")

    text = [
        "❔ Частые вопросы\n",
    ]

    if callback_data.question_id == 1:
        text.extend([
            "ℹ️ Как работает накрутка ПФ\n",
            "Ответ на 1 вопрос"
        ])

    elif callback_data.question_id == 2:
        text.extend([
            "ℹ️ Лучшая методика накрутки\n",
            "Ответ на 2 вопрос"
        ])

    elif callback_data.question_id == 3:
        text.extend([
            "ℹ️ ПФ на объявления в аккаунте одним днём\n",
            "Ответ на 3 вопрос"
        ])

    else:
        text.extend([
            "Нету ответа на вопрос!"
        ])

    text.append("\n⬇️ Используйте клавиатуру ниже")

    markup = await Im.back(callback_data="back_from_question_answer")
    await Ut.send_step_message(user_id=uid, text="\n".join(text), markup=markup)
