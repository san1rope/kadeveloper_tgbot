import logging
import traceback
from typing import Optional, Union, List

from sqlalchemy import and_
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
    def __init__(
            self, db_id: Optional[int] = None, tg_user_id: Optional[int] = None, status: Optional[int] = None,
            period: Optional[int] = None, pf: Optional[int] = None, advert_url: Optional[str] = None,
            api_id: Optional[int] = None
    ):
        self.db_id = db_id
        self.api_id = api_id
        self.tg_user_id = tg_user_id
        self.status = status
        self.period = period
        self.pf = pf
        self.advert_url = advert_url

    async def add(self) -> Union[bool, Order]:
        try:
            target = Order(tg_user_id=self.tg_user_id, status=self.status, period=self.period, pf=self.pf,
                           advert_url=self.advert_url, api_id=self.api_id)
            return await target.create()

        except UniqueViolationError:
            return False

    async def select(self) -> Union[bool, Order, List[Order], None]:
        try:
            q = Order.query

            if self.db_id is not None:
                return await q.where(Order.id == self.db_id).gino.first()

            elif self.tg_user_id is not None and self.status is not None:
                return await q.where(and_(Order.tg_user_id == self.tg_user_id, Order.status == self.status)).gino.all()

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


class DbTempOrder:
    def __init__(self, db_id: Optional[int] = None, tg_user_id: Optional[int] = None,
                 current_state: Optional[str] = None, period: Optional[int] = None, pf: Optional[int] = None,
                 adverts_urls: Optional[List[str]] = None, price: Optional[float] = None):
        self.db_id = db_id
        self.tg_user_id = tg_user_id
        self.current_state = current_state
        self.period = period
        self.pf = pf
        self.adverts_urls = adverts_urls
        self.price = price

    async def add(self) -> Union[TempOrder, bool]:
        try:
            target = TempOrder(tg_user_id=self.tg_user_id, current_state=self.current_state, period=self.period,
                               pf=self.pf, adverts_urls=self.adverts_urls, price=self.price)
            return await target.create()

        except UniqueViolationError:
            return False

    async def select(self) -> Union[bool, TempOrder, List[TempOrder], None]:
        try:
            q = TempOrder.query

            if self.db_id is not None:
                return await q.where(TempOrder.id == self.db_id).gino.first()

            elif self.tg_user_id is not None:
                return await q.where(TempOrder.tg_user_id == self.tg_user_id).gino.first()

            else:
                return await q.gino.all()

        except Exception:
            logger.error(traceback.format_exc())
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

    # async def remove(self) -> Union[bool, List[bool]]:
    #     try:
    #         target = await self.select()
    #         if isinstance(target, list):
    #             results = []
    #             for i in target:
    #                 results.append(await i.delete())
    #
    #             return results
    #
    #         elif isinstance(target, TempOrder):
    #             return await target.delete()
    #
    #     except Exception:
    #         logger.error(traceback.format_exc())
    #         return False


class DbPayment:
    def __init__(self, db_id: Optional[int] = None, tg_user_id: Optional[int] = None, price: Optional[int] = None,
                 confirmation: Optional[int] = None, data: Optional[str] = None):
        self.db_id = db_id
        self.tg_user_id = tg_user_id
        self.price = price
        self.confirmation = confirmation
        self.data = data

    async def add(self) -> Union[bool, Payment]:
        try:
            target = Payment(tg_user_id=self.tg_user_id, confirmation=self.confirmation, data=self.data,
                             price=self.price)
            return await target.create()

        except UniqueViolationError:
            return False

    async def select(self):
        try:
            q = Payment.query

            if self.db_id is not None:
                return await q.where(Payment.id == self.db_id).gino.first()

            elif self.tg_user_id is not None:
                return await q.where(Payment.tg_user_id == self.tg_user_id).gino.all()

            elif self.confirmation:
                return await q.where(Payment.confirmation == self.confirmation).gino.all()

            else:
                return await q.gino.all()

        except Exception:
            logger.error(traceback.format_exc())
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
