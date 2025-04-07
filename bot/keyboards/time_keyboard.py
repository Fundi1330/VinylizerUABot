from telegram import InlineKeyboardButton
from bot.config import logger

def generate_time_keyboard(audio_length: int) -> list:
    keyboard = [
        [InlineKeyboardButton('🕛З початку', callback_data='0')]
    ]
    periods = int(audio_length // 15)
    time = 0

    for i in range(periods):
        time += 15
        minutes = time // 60
        seconds = time % 60
        time_str = '⌛'
        if minutes == 0:
            time_str += '00'
        else:
            time_str += f'0{minutes}'
        time_str += ':'
        if seconds == 0:
            time_str += '00'
        else:
            time_str += str(seconds)

        keyboard.append(
            [InlineKeyboardButton(time_str, callback_data=f'{time}')]
        )
    return keyboard