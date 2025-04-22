import asyncio
import logging
from typing import Optional, Union

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from config import Config
from tg_bot.db_models.schemas import Payment
from tg_bot.keyboards.inline import InlineMarkups as Im

logger = logging.getLogger(__name__)
msg_to_delete = {"secondary": {}}


class Utils:

    @staticmethod
    def wrapper(func, *args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    @classmethod
    async def parse_advertisement(cls, url: str, retries: int = 3):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://www.avito.ru/",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Opera GX";v="117"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0"
        }

        try:
            async with ClientSession() as session:
                async with session.get(url=url, headers=headers, timeout=10) as response:
                    answer = await response.text()

            soup = BeautifulSoup(answer, "lxml")
            name = soup.find("h1", {"itemprop": "name"}).text
            category = soup.find("div", {"data-marker": "item-navigation"}).text.strip()
            location = soup.find("div", {"itemprop": "address"}).text

            return name, category, location

        except Exception as ex:
            if retries <= 0:
                return None, None, None

            logger.error(f"Не удалось спарсить объявление! | Осталось попыток: {retries} | {url} | {ex}")
            return await cls.parse_advertisement(url=url, retries=retries - 1)

    @staticmethod
    async def send_step_message(user_id: int, text: str, markup: Optional[InlineKeyboardMarkup] = None):
        await Utils.delete_messages(user_id=user_id)
        msg = await Config.BOT.send_message(chat_id=user_id, text=text, reply_markup=markup,
                                            disable_web_page_preview=True)
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

    @staticmethod
    async def verify_advertisement_url(url: str) -> bool:
        if not url.startswith("https://www.avito.ru/"):
            return False

        return True

    @staticmethod
    async def send_payment_confirmation_to_admins(payment: Payment, price: int):
        text = [
            "❇️ Поступил новый заказ!\n",
            f"Была произведена оплата на сумму {price} рублей!\n",
            "Проверьте платеж и подтвердите создание заказа"
        ]
        markup = await Im.
