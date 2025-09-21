from aiogram.fsm.state import State, StatesGroup

class Checkout(StatesGroup):
    """
    FSM states for the checkout process.
    """
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    confirming_order = State()

class AdminProduct(StatesGroup):
    """
    FSM states for the admin adding a new product.
    """
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_quantity = State()
    waiting_for_category = State()
    waiting_for_image = State()
