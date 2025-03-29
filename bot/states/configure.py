from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.keyboards import configure_keyboard
from .configure_decision import CONFIGURE_DECISION
from bot.config import config, logger
from os import makedirs

CONFIGURE = 0


async def configure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Asks user to configure the music'''
    user = update.effective_user
    audio = update.message.audio
    audio_name = audio.file_name

    logger.info('User started vinylization')

    context.user_data['music_name'] = audio_name

    file_id = audio.file_id
    new_file = await context.bot.get_file(file_id)
    save_folder = f'bot/assets/user_audios/{user.username}_{user.id}/'
    makedirs(save_folder, exist_ok=True)

    await new_file.download_to_drive(f'{save_folder}/{audio_name}')

    text = '''
    Оберіть, що ви хочете робити далі👇.
    '''
    reply_markup = InlineKeyboardMarkup(configure_keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return CONFIGURE_DECISION