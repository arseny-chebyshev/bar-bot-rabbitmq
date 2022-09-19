import operator
from db.models import Dish
from filters.base import is_button_selected
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Radio, Button, Group, ManagedRadioAdapter
from aiogram_dialog.widgets.text import Format, Const
from states.admin import DishDialog, DishState
from keyboards.menu.kbds import cancel_menu_button
from keyboards.dialog.base_dialog_buttons import cancel_button, continue_button, back_button, default_nav, back_to_start_button

async def select_dish_menu(c: CallbackQuery, b: Button, d: DialogManager):
    match b.widget_id:
        case 'new_dish':
            await d.data['state'].reset_state(with_data=True)
            await c.message.delete()
            await c.message.answer("Введи имя новой позиции: ", reply_markup=cancel_menu_button)
            await DishState.insert_name.set()
        case 'dish_list':
            await d.start(DishDialog.select_dish)

dish_start = Window(Const("Пожалуйста, выбери действие:"),
                    Group(Button(Const("Создать новую позицию"),
                                     id="new_dish", on_click=select_dish_menu),
                          Button(Const("Изменить/удалить текущие позиции"),
                                     id="dish_list", on_click=select_dish_menu),
                              width=1),
                          back_to_start_button,
                        state=DishDialog.start)

async def get_dishes(**kwargs):
    return {"dishes": [(str(dish), dish.id) for dish in Dish.objects.all()]}

async def switch_to_dish_details(c: CallbackQuery, m: ManagedRadioAdapter, d: DialogManager,  b: Button):
    await d.switch_to(DishDialog.edit_dish)

dish_list = Window(Const("Выбери позицию из списка:"),
                         Group(Radio(Format("{item[0]}"),
                                       Format("{item[0]}"),
                                       id="r_dish", items='dishes', on_click=switch_to_dish_details,
                                       item_id_getter=operator.itemgetter(1)),
                                 width=2),
                         default_nav,
                         getter=get_dishes,
                         state=DishDialog.select_dish)

async def get_dish_detail(**kwargs):
    dish_id = kwargs['aiogd_context'].widget_data['r_dish']
    return {"dish": Dish.objects.filter(id=dish_id).first()}

async def switch_edit_dish(c: CallbackQuery, b: Button, d: DialogManager):
    match b.widget_id:
        case "edit":
            old_dish = Dish.objects.filter(id=int(d.data['aiogd_context'].widget_data.pop('r_dish'))).first()
            dish_id = old_dish.id
            await d.data['state'].reset_state(with_data=True)
            await c.message.delete()
            await c.message.answer(f"Старое имя: {old_dish.name}\nСтарая цена: {old_dish.price} LKR\nВведи новое имя:")
            await DishState.insert_name.set()
            await d.data['state'].update_data({"old_dish": dish_id})
        case "delete":
            dish_id = d.data['aiogd_context'].widget_data['r_dish']
            dish = Dish.objects.filter(id=dish_id).first()
            dish_name = dish.name
            dish.delete()
            await c.message.delete()
            await c.message.answer(f"Позиция {dish_name} удалена.")
            d.data['aiogd_context'].widget_data.pop('r_dish')
            await d.switch_to(DishDialog.select_dish)

dish_detail =  Window(Format(text="{dish.name}, {dish.price}"),
                             Group(Button(Const("Изменить"), on_click=switch_edit_dish, id="edit"),
                                   Button(Const("Удалить"), on_click=switch_edit_dish, id="delete"),
                                   width=2),
                          back_button,
                          cancel_button,
                      getter=get_dish_detail,
                      state=DishDialog.edit_dish)

dish_dialog = Dialog(dish_start, dish_list, dish_detail)