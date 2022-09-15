import operator
from db.models import Order
from filters.base import is_button_selected
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Back, Next
from aiogram_dialog.widgets.text import Format, Const
from states.admin import DishDialog, DishState, OrderDialog
from keyboards.dialog.base_dialog_buttons import cancel_button, continue_button, back_button, default_nav, back_to_start_button

async def get_orders(**kwargs):
    return {"orders": [(str(order), order.id) for order in Order.objects.all()]}

async def switch_to_details(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(OrderDialog.edit_order)

order_list = Window(Const("Выбери заказ из списка:"),
                         Group(Radio(Format("✅{item[0]}"),
                                     Format("{item[0]}"),
                                       id="r_order", items='orders',
                                       item_id_getter=operator.itemgetter(1)),
                                 width=1),
                         Button(continue_button,
                                on_click=switch_to_details,
                                id='continue'),
                         back_to_start_button,
                         getter=get_orders,
                         state=OrderDialog.select_order)


async def get_order_detail(**kwargs):
    order_id = kwargs['aiogd_context'].widget_data['r_order']
    return {"order": Order.objects.filter(id=order_id)[0]}

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
            order_name = order.id
            order.delete()
            await c.message.delete()
            await c.message.answer(f"Заказ {order} удален.")
            d.data['aiogd_context'].widget_data.pop('r_order')
            await d.switch_to(OrderDialog.select_order)

order_detail =  Window(Format(text="{order}"),
                             Group(Button(Const("Отметить готовым"), on_click=switch_edit_order, id="done"),
                                   Button(Const("Удалить"), on_click=switch_edit_order, id="delete"),
                                   width=2),
                          back_button,
                      getter=get_order_detail,
                      state=OrderDialog.edit_order)

order_dialog = Dialog(order_list, order_detail)