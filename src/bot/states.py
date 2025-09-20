from aiogram.fsm.state import State, StatesGroup

class OrderPlacement(StatesGroup):
    """
    Finite State Machine for the order placement process.
    """
    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_coupon = State()
    waiting_for_confirmation = State()
