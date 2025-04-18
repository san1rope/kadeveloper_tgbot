import logging
from typing import Optional, Union

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup

from config import Config

logger = logging.getLogger(__name__)
msg_to_delete = {"secondary": {}}


class Utils:

    @staticmethod
    async def send_step_message(user_id: int, text: str, markup: Optional[InlineKeyboardMarkup] = None):
        await Utils.delete_messages(user_id=user_id)
        msg = await Config.BOT.send_message(chat_id=user_id, text=text, reply_markup=markup)
        await Utils.add_msg_to_delete(user_id=user_id, msg_id=msg.message_id)

        return msg

    @staticmethod
    async def add_msg_to_delete(user_id: Union[str, int], msg_id: Union[str, int], secondary: bool = False):
        try:
            if secondary:
                if user_id not in msg_to_delete["secondary"]:
                    msg_to_delete["secondary"][user_id] = []

                msg_to_delete["secondary"][user_id].append(msg_id)
                return

            if user_id not in msg_to_delete:
                msg_to_delete[user_id] = []

            msg_to_delete[user_id].append(msg_id)

        except Exception as ex:
            logger.error(f"Couldn't add msg_id to msg_to_delete\n{ex}")

    @staticmethod
    async def delete_messages(user_id: Optional[int] = None, secondary: bool = False):
        try:
            if not user_id:
                for uid in msg_to_delete:
                    for msg_id in msg_to_delete.get(uid):
                        try:
                            await Config.BOT.delete_message(chat_id=uid, message_id=msg_id)
                        except TelegramBadRequest:
                            continue

                return

            if secondary:
                for msg_id in msg_to_delete["secondary"][user_id]:
                    try:
                        await Config.BOT.delete_message(chat_id=user_id, message_id=msg_id)
                    except TelegramBadRequest:
                        continue

            else:
                for msg_id in msg_to_delete[user_id]:
                    try:
                        await Config.BOT.delete_message(chat_id=user_id, message_id=msg_id)
                    except TelegramBadRequest:
                        continue

            msg_to_delete[user_id].clear()
        except KeyError:
            return
