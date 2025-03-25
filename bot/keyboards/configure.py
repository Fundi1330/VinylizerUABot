from telegram import InlineKeyboardButton

configure_keyboard = [
    [InlineKeyboardButton('Продовжити', callback_data='Continue')],
    [InlineKeyboardButton('Додатково налаштувати(поки що не працює)', callback_data='Configure')]
]
