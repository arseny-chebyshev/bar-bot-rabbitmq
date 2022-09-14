from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


def is_button_selected(key: str = None):
    def wrapper(async_func):
        async def _wrapper(c: CallbackQuery, b: Button, d: DialogManager):
            if d.data['aiogd_context'].widget_data[key]:
                await async_func(c, b, d)
            else:
                await c.answer("Сначала нужно выбрать одну из опций")
        return _wrapper
    return wrapper
