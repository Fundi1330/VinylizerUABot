from telegram import InlineKeyboardButton

yes_no_keyboard = [
    [InlineKeyboardButton('✅Так!', callback_data='Yes')],
    [InlineKeyboardButton('❌Ні!', callback_data='No')]
]
