from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from filters.base import is_button_selected
from keyboards.menu.kbds import request_contact_button_kbd


async def cancel(c: CallbackQuery, b: Button, d: DialogManager):
    await c.message.delete()
    await c.message.answer(text=f"Действие отменено.")
    await d.mark_closed()
    await d.data['state'].reset_state(with_data=True)


async def erase_widget_data(c: CallbackQuery, b: Button, d: DialogManager):
    d.data['aiogd_context'].widget_data = {}


async def require_contact():
    pass