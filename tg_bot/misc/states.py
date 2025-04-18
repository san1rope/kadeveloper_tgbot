from aiogram.fsm.state import StatesGroup, State


class CreateOrder(StatesGroup):
    ChoosePeriod = State()
    ChoosePFQuantity = State()
    InsertAdvertsUrls = State()
    MakePayment = State()
