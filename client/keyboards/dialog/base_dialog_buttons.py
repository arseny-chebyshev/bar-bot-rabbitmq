from aiogram_dialog.widgets.kbd import Radio, Button, Group, Back, Next
from aiogram_dialog.widgets.text import Format, Const
from .actions import cancel, erase_widget_data

cancel_button = Button(Const("❌ Отмена"), id='cancel', on_click=cancel)
back_button = Back(Const("⬅ Назад"))
back_to_start_button = Button(Const("⬅ Назад"), id='back_to_start', on_click=erase_widget_data)
continue_button = Const("Продолжить ➡")
default_nav = Group(back_button, cancel_button, width=2)
