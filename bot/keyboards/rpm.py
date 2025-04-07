from telegram import InlineKeyboardButton

rpm_keyboard = [
    [   
        InlineKeyboardButton('💫3 Оберти', callback_data='3'),
        InlineKeyboardButton('💫6 Обертів', callback_data='6'),
        InlineKeyboardButton('⭐10 Обертів', callback_data='10'),
    ],
    [
        InlineKeyboardButton('💫24 Оберти', callback_data='24'),
        InlineKeyboardButton('💫36 Обертів', callback_data='36'),
        InlineKeyboardButton('💫72 Оберти', callback_data='72')
    ]
    
]
