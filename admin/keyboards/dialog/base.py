import operator
from db.models import Dish
from filters.base import is_button_selected
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Back, Next
from aiogram_dialog.widgets.text import Format, Const
from states.admin import DishDialog, OrderDialog, AdminDialog, StatDialog
from keyboards.dialog.base_dialog_buttons import cancel_button, continue_button, back_button, default_nav

async def select_menu(c: CallbackQuery, b: Button, d: DialogManager):
    match b.widget_id:
        case 'get_dishes':
            await d.start(DishDialog.start)
        case 'get_orders':
            await d.start(OrderDialog.start)
        case 'get_stats':
            await d.start(StatDialog.start)

start_menu = Window(Const("""Пожалуйста, выбери действие:"""),
                        Group(Button(Const("Меню"),
                                     id="get_dishes", on_click=select_menu),
                              Button(Const("Заказы"),
                                     id="get_orders", on_click=select_menu),
                              Button(Const("Статистика"),
                                     id="get_stats", on_click=select_menu), width=2),
                              cancel_button,
                        state=AdminDialog.start)

start_dialog = Dialog(start_menu,)
