from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

request_contact_button_kbd = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🖊 Заказать", request_contact=True)],
], resize_keyboard=True, one_time_keyboard=True)

new_order_button_kbd = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🖊 Заказать")],
], resize_keyboard=True, one_time_keyboard=True)

dish_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить новую позицию')],
    [KeyboardButton(text='Изменить текущие позиции')],
],  resize_keyboard=True, one_time_keyboard=True)

confirm_dish_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Подтвердить')],
    [KeyboardButton(text='Отмена')],
],  resize_keyboard=True, one_time_keyboard=True)
