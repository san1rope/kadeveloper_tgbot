from sqlalchemy import sql, Column, BigInteger, String, Integer, ARRAY

from tg_bot.db_models.db_gino import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = "users_kadeveloper_tgbot"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False, primary_key=True)
    balance = Column(Integer, nullable=False)

    query: sql.Select


class Order(TimedBaseModel):
    __tablename__ = "orders_kadeveloper_tgbot"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    api_id = Column(BigInteger, nullable=False, primary_key=True)
    tg_user_id = Column(BigInteger, nullable=False, primary_key=True)
    status = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    pf = Column(Integer, nullable=False)
    advert_url = Column(String, nullable=False)

    query: sql.Select


class TempOrder(TimedBaseModel):
    __tablename__ = "temp_orders_kadeveloper_tgbot"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False, primary_key=True)
    current_state = Column(String)
    period = Column(Integer)
    pf = Column(Integer)
    adverts_urls = Column(ARRAY(String))
    price = Column(Integer)

    query: sql.Select


class MessageId(TimedBaseModel):
    __tablename__ = "messages_kadeveloper_tgbot"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False)
    telegram_id = Column(BigInteger, nullable=False)

    query: sql.Select


class Payment(TimedBaseModel):
    __tablename__ = "payments_kadeveloper_tgbot"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False)
    price = Column(Integer, nullable=False)
    confirmation = Column(Integer, nullable=False)
    data = Column(String, nullable=False)

    query: sql.Select
