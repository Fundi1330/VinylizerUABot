from telegram import InlineKeyboardButton
from bot.config import logger
from bot.core.utils import get_vinyl_list

vinyl_keyboard = []
row = []

vinyl_list = get_vinyl_list()

for ind, vyn in enumerate(vinyl_list):
    number = ind + 1
    row.append(
        InlineKeyboardButton(number + '🔒' if vyn['is_premium'] else number, callback_data=f'{ind}') # if the vinyl is premium - add the locked emoji
    )
    if len(row) >= 2:
        vinyl_keyboard.append(row)
        row = []
if len(row) > 0:
    vinyl_keyboard.append(row)