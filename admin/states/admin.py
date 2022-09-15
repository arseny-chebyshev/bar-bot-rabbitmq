from aiogram.dispatcher.filters.state import StatesGroup, State

class AdminDialog(StatesGroup):
    start = State()

class DishDialog(StatesGroup):
    start = State()
    select_dish = State()
    edit_dish = State()
    confirm_delete_dish = State()

class DishState(StatesGroup):
    select_dish_action = State()
    insert_name = State()
    insert_price = State()
    confirm_dish = State()

class OrderDialog(StatesGroup):
    select_order = State()
    edit_order = State()
    confirm_edit = State()

class StatDialog(StatesGroup):
    start = State()
    list_guest_total = State()
    guest_detail = State()
    list_dish_total = State()

class RegisterUser(StatesGroup):
    send_contact = State()
