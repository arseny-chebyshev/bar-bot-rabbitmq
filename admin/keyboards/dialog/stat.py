import operator
from db.models import Order, Guest
from filters.base import is_button_selected
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Back, Next
from aiogram_dialog.widgets.text import Format, Const
from states.admin import DishDialog, DishState, StatDialog
from keyboards.dialog.base_dialog_buttons import cancel_button, continue_button, back_button, default_nav, back_to_start_button

async def select_stat_menu(c: CallbackQuery, b: Button, d: DialogManager):
    match b.widget_id:
        case 'guest_stat':
            await d.start(StatDialog.list_guest_total)
        case 'dish_stat':
            await d.start(StatDialog.list_dish_total)

stat_start = Window(Const("Пожалуйста, выбери действие:"),
                    Group(Button(Const("Статистика по гостям"),
                                     id="guest_stat", on_click=select_stat_menu),
                          Button(Const("Статистика по позициям"),
                                     id="dish_stat", on_click=select_stat_menu),
                              width=1),
                          back_to_start_button,
                        state=StatDialog.start)

async def get_guests(**kwargs):
    guests = Guest.objects.all()
    return {"guests": [(guest, guest.id) for guest in guests]}

async def switch_to_guest_details(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(StatDialog.guest_detail)

guest_stat = Window(Const("Выбери гостя из списка:"),
                         Group(Radio(Format("✅{item[0]}"),
                                     Format("{item[0]}"),
                                     id="r_guest", items='guests',
                                     item_id_getter=operator.itemgetter(1)),
                               width=2),
                         Button(continue_button,
                                on_click=switch_to_guest_details,
                                id='continue'),
                         default_nav,
                         getter=get_guests,
                         state=StatDialog.list_guest_total)

stat_dialog = Dialog(stat_start, guest_stat)
