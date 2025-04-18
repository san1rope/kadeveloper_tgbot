from sqlalchemy import sql, Column, BigInteger, String, Integer, DateTime, Float, Boolean
from sqlalchemy.dialects.postgresql import ARRAY

from tg_bot.db_models.db_gino import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False, primary_key=True)
    balance = Column(Integer, nullable=False)

    query: sql.Select


class Order(TimedBaseModel):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False, primary_key=True)
    status = Column(Boolean, nullable=False)
    period = Column(Integer, nullable=False)
    pf = Column(Integer, nullable=False)
    adverts_urls = Column(ARRAY(String), nullable=False)

    query: sql.Select
