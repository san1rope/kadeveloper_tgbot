import json
import logging
import base64
from typing import Dict, Any

from aiohttp import BasicAuth, ClientSession

from config import Config
from tg_bot.misc.models import APIUser, APIOrder

logger = logging.getLogger(__name__)


class APIInterface:
    url = Config.API_URL
    headers = {
        "Content-Type": "text/plain; charset=UTF-8"
    }

    @staticmethod
    async def encode_json_payload(payload: Dict) -> str:
        json_payload = json.dumps(payload)
        encoded_once = base64.b64encode(json_payload.encode()).decode()
        return base64.b64encode(encoded_once.encode()).decode()

    @staticmethod
    async def decode_json_answer(data: str) -> Dict:
        for i in range(2):
            decoded_bytes = base64.b64decode(data)
            data = decoded_bytes.decode('utf-8')

        return json.loads(data)

    @classmethod
    async def add_or_update_new_user(cls, api_user: APIUser) -> Dict:
        encoded_data = await cls.encode_json_payload(
            {
                'run': 'get_profile',
                'data': api_user.model_dump()
            }
        )

        async with ClientSession() as session:
            async with session.post(url=cls.url, headers=cls.headers, data=encoded_data, timeout=20) as response:
                answer = await response.text()

        result = await cls.decode_json_answer(answer)
        logger.info(f"Request to API | get_profile | {result}")
        return result

    @classmethod
    async def add_or_update_new_task(cls, api_order: APIOrder) -> Dict:
        encoded_data = await cls.encode_json_payload(
            {
                "run": "save_task",
                "data": api_order.model_dump()
            }
        )

        async with ClientSession() as session:
            async with session.post(url=cls.url, headers=cls.headers, data=encoded_data, timeout=20) as response:
                answer = await response.text()

        result = await cls.decode_json_answer(answer)
        logger.info(f"Request to API | save_task | {result}")
        return result
