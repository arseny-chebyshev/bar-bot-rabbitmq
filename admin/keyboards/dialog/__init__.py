from tracemalloc import start
from keyboards.dialog.base import start_dialog
from keyboards.dialog.dish import dish_dialog
from keyboards.dialog.order import order_dialog
from keyboards.dialog.stat import stat_dialog
dialogs = [start_dialog, dish_dialog, order_dialog, stat_dialog]