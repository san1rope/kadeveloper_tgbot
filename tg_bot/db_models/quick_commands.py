import logging
import traceback
from typing import Optional, Union, List

from asyncpg import UniqueViolationError

from .schemas import *

logger = logging.getLogger(__name__)


class DbUser:
    def __init__(self, db_id: Optional[int] = None, tg_user_id: Optional[int] = None, balance: Optional[int] = None):
        self.db_id = db_id
        self.tg_user_id = tg_user_id
        self.balance = balance

    async def add(self) -> Union[bool, User]:
        try:
            target = User(tg_user_id=self.tg_user_id, balance=self.balance)
            return await target.create()

        except UniqueViolationError:
            return False

    async def select(self):
        try:
            q = User.query

            if self.db_id is not None:
                return await q.where(User.id == self.db_id).gino.first()

            elif self.tg_user_id is not None:
                return await q.where(User.tg_user_id == self.tg_user_id).gino.first()

            else:
                return await q.gino.all()

        except Exception:
            return False

    async def update(self, **kwargs) -> bool:
        try:
            if not kwargs:
                return False

            target = await self.select()
            return await target.update(**kwargs).apply()

        except Exception:
            logger.error(traceback.format_exc())
            return False

    async def remove(self) -> Union[bool, List[bool]]:
        try:
            target = await self.select()
            if isinstance(target, list):
                results = []
                for i in target:
                    results.append(await i.delete())

                return results

            elif isinstance(target, User):
                return await target.delete()

        except Exception:
            logger.error(traceback.format_exc())
            return False


class DbOrder:
    def __init__(self, db_id: Optional[int] = None, tg_user_id: Optional[int] = None, status: Optional[bool] = None,
                 period: Optional[int] = None, pf: Optional[int] = None, adverts_urls: Optional[List[str]] = None):
        self.db_id = db_id
        self.tg_user_id = tg_user_id
        self.status = status
        self.period = period
        self.pf = pf
        self.adverts_urls = adverts_urls

    async def add(self) -> Union[bool, Order]:
        try:
            target = Order(tg_user_id=self.tg_user_id, status=self.status, period=self.period, pf=self.pf,
                           adverts_urls=self.adverts_urls)
            return await target.create()

        except UniqueViolationError:
            return False

    async def select(self):
        try:
            q = Order.query

            if self.db_id is not None:
                return await q.where(Order.id == self.db_id).gino.first()

            elif self.tg_user_id is not None:
                return await q.where(Order.tg_user_id == self.tg_user_id).gino.all()

            elif self.status is not None:
                return await q.where(Order.status == self.status).gino.all()

            else:
                return await q.gino.all()

        except Exception:
            return False

    async def update(self, **kwargs) -> bool:
        try:
            if not kwargs:
                return False

            target = await self.select()
            return await target.update(**kwargs).apply()

        except Exception:
            logger.error(traceback.format_exc())
            return False

    async def remove(self) -> Union[bool, List[bool]]:
        try:
            target = await self.select()
            if isinstance(target, list):
                results = []
                for i in target:
                    results.append(await i.delete())

                return results

            elif isinstance(target, Order):
                return await target.delete()

        except Exception:
            logger.error(traceback.format_exc())
            return False
