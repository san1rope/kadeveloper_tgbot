import json
import logging
import base64
from typing import Dict

from aiohttp import BasicAuth, ClientSession

from config import Config
from tg_bot.misc.models import APIUser

logger = logging.getLogger(__name__)


class APIInterface:
    url = Config.API_URL
    headers = {
        "Content-Type": "text/plain; charset=UTF-8"
    }
    proxy = "http://156.246.211.231:64170"
    proxy_auth = BasicAuth(login="ttNkVLRS", password="63cYXNdr")

    @classmethod
    async def add_new_user(cls, api_user: APIUser) -> Dict:
        data = {
            'run': 'get_profile',
            'data': api_user.model_dump()
        }

        json_payload = json.dumps(data)
        encoded_once = base64.b64encode(json_payload.encode()).decode()
        encoded_twice = base64.b64encode(encoded_once.encode()).decode()

        async with ClientSession() as session:
            async with session.post(
                    url=cls.url, headers=cls.headers, data=encoded_twice, proxy=cls.proxy, proxy_auth=cls.proxy_auth, timeout=20
            ) as response:
                answer = await response.text()
                for i in range(2):
                    decoded_bytes = base64.b64decode(answer)
                    answer = decoded_bytes.decode('utf-8')

        return json.loads(answer)
