import operator
from db.models import Order, Guest, Dish
from filters.base import is_button_selected
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Radio, Button, Group, ManagedRadioAdapter
from aiogram_dialog.widgets.text import Format, Const
from states.admin import StatDialog
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

async def switch_to_guest_details(c: CallbackQuery, r: ManagedRadioAdapter, d: DialogManager, b: Button):
    await d.switch_to(StatDialog.guest_detail)

async def switch_to_guest_list(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(StatDialog.start)

guest_stat = Window(Const("Выбери гостя из списка:"),
                         Group(Radio(Format("{item[0]}"),
                                     Format("{item[0]}"),
                                     id="r_guest", items='guests', on_click=switch_to_guest_details,
                                     item_id_getter=operator.itemgetter(1)),
                               width=1),
                         Button(Const("⬅ Назад"), id='_back', on_click=switch_to_guest_list),
                         getter=get_guests,
                         state=StatDialog.list_guest_total)

async def get_guest_details(**kwargs):
    guest = Guest.objects.filter(id=kwargs['aiogd_context'].widget_data['r_guest']).first()
    return {"guest": guest, "guest_orders": '\n'.join([str(order) for order 
                                                       in guest.orders_from_guest.all()])}

async def reset_debt(c: CallbackQuery, b: Button, d: DialogManager):
    guest = Guest.objects.filter(id=d.data['aiogd_context'].widget_data['r_guest']).first()
    guest.debt = 0
    guest.save()
    await d.switch_to(StatDialog.list_guest_total)

guest_detail =  Window(Format(text="{guest}\nЗаказы:\n{guest_orders}\n\nБаланс: {guest.debt} LKR"), 
                       Button(Const("Сбросить баланс гостя"), id='reset_debt', on_click=reset_debt),        
                       back_button,
                       cancel_button,
                       getter=get_guest_details,
                       state=StatDialog.guest_detail)

async def get_dishes(**kwargs):
    dishes = Dish.objects.all()
    quantities = [dish.get_summary() for dish in dishes]
    return {"stat": '\n'.join([f"{dish.name}: {quant if quant else 0}" for dish, quant in zip(dishes, quantities)])}

dish_stat = Window(Const("Общее количество заказов для каждой позиции:"),
                   Format("{stat}"),
                   default_nav,
                   getter=get_dishes,
                   state=StatDialog.list_dish_total)

stat_dialog = Dialog(stat_start, dish_stat, guest_stat, guest_detail)
