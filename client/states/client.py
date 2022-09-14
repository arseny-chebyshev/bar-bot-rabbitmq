from aiogram.dispatcher.filters.state import StatesGroup, State

class DishDialog(StatesGroup):
    select_dish = State()
    edit_dish_quantity = State()
    confirm_order = State()

class DishState(StatesGroup):
    select_dish_action = State()
    insert_name = State()
    insert_price = State()
    confirm_dish = State()

class OrderDialog(StatesGroup):
    select_order = State()
    edit_order = State()
    confirm_edit = State()

class StatState(StatesGroup):
    select_stat = State()
    list_guest_total = State()
    list_dished_total = State()

class RegisterUser(StatesGroup):
    send_contact = State()
