import operator
from db.models import DishQuantity, Order
from filters.base import is_button_selected
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Back, Next, ManagedRadioAdapter
from aiogram_dialog.widgets.text import Format, Const
from states.admin import DishDialog, DishState, OrderDialog
from keyboards.dialog.base_dialog_buttons import cancel_button, continue_button, back_button, default_nav, back_to_start_button

async def select_order_menu(c: CallbackQuery, b: Button, d: DialogManager):
    match b.widget_id:
        case 'ready':
            d.data['aiogd_context'].widget_data['order_status'] = True
        case 'not_ready':
            d.data['aiogd_context'].widget_data['order_status'] = False
    await d.switch_to(OrderDialog.select_order)

order_start = Window(Const("Пожалуйста, выбери категорию:"),
                    Group(Button(Const("Ожидающие заказы"),
                                     id="not_ready", on_click=select_order_menu),
                          Button(Const("Готовые заказы"),
                                     id="ready", on_click=select_order_menu),
                              width=1),
                          back_to_start_button,
                        state=OrderDialog.start)

async def get_orders(**kwargs):
    status = kwargs['aiogd_context'].widget_data['order_status']
    orders = Order.objects.all().filter(is_ready=status)
    return {"orders": [(str(order), order.id) for order in orders]}

async def switch_to_details(c: CallbackQuery, r: ManagedRadioAdapter, d: DialogManager, b: Button):
    await d.switch_to(OrderDialog.edit_order)

order_list = Window(Const("Выбери заказ из списка:"),
                         Group(Radio(Format("{item[0]}"),
                                     Format("{item[0]}"),
                                       id="r_order", items='orders', on_click=switch_to_details,
                                       item_id_getter=operator.itemgetter(1)),
                                 width=1),
                         default_nav,
                         getter=get_orders,
                         state=OrderDialog.select_order)


async def get_order_detail(**kwargs):
    order_id = kwargs['aiogd_context'].widget_data['r_order']
    order = Order.objects.filter(id=order_id).first()
    order_text = f"{order}:\n" + '\n'.join([f'{dish.dish.name} x {dish.quantity}: {dish.dish.price * dish.quantity}' for dish in DishQuantity.objects.filter(order=order)])
    order_text += f"\nИтого: {order.total}"
    return {"order": order_text, 'is_not_ready': not kwargs['aiogd_context'].widget_data['order_status']}

async def switch_edit_order(c: CallbackQuery, b: Button, d: DialogManager):
    match b.widget_id:
        case "done":
            order_id = d.data['aiogd_context'].widget_data['r_order']
            order = Order.objects.filter(id=order_id).first()
            order.is_ready = True
            order.save()
            await d.switch_to(OrderDialog.select_order)
        case "delete":
            order_id = d.data['aiogd_context'].widget_data['r_order']
            order = Order.objects.filter(id=order_id).first()
            order_id = order.id
            order.delete()
            await c.message.delete()
            await c.message.answer(f"Заказ #{order_id} удален.")
            d.data['aiogd_context'].widget_data.pop('r_order')
            await d.switch_to(OrderDialog.select_order)

order_detail =  Window(Format(text="{order}"),
                             Group(Button(Const("Отметить готовым"), on_click=switch_edit_order, 
                                                                     id="done", when='is_not_ready'),
                                   Button(Const("Удалить"), on_click=switch_edit_order, id="delete"),
                                   width=2),
                          back_button,
                      getter=get_order_detail,
                      state=OrderDialog.edit_order)

order_dialog = Dialog(order_start, order_list, order_detail)