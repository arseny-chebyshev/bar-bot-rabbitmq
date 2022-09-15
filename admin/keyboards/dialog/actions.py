from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from filters.base import is_button_selected
from states.admin import AdminDialog
from keyboards.menu.kbds import request_phone_button_kbd


async def cancel(c: CallbackQuery, b: Button, d: DialogManager):
    await c.message.delete()
    await c.message.answer(text=f"Действие отменено.")
    await d.mark_closed()
    await d.data['state'].reset_state(with_data=True)


async def erase_widget_data(c: CallbackQuery, b: Button, d: DialogManager):
    await d.mark_closed()
    await d.data['state'].reset_state(with_data=True)
    await d.start(AdminDialog.start)

async def require_contact():
    pass