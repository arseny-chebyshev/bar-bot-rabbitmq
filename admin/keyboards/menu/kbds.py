from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

request_phone_button_kbd = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🖊 Заказать", request_contact=True), KeyboardButton(text="❌ Отмена")],
], resize_keyboard=True)

dish_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='➕Добавить новую позицию')],
    [KeyboardButton(text='🖊Изменить текущие позиции')],
],  resize_keyboard=True, one_time_keyboard=True)

cancel_menu_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='❌Отмена')],
],  resize_keyboard=True, one_time_keyboard=True)

confirm_dish_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='✅Подтвердить')],
    [KeyboardButton(text='❌Отмена')],
],  resize_keyboard=True, one_time_keyboard=True)
