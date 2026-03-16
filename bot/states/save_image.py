from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.config import logger
from bot.core.utils import get_cover_path
from .rpm import RPM
from bot.keyboards import rpm_keyboard
import os
import uuid

SAVE_IMAGE = 4


async def save_image_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Saves the album image'''
    photo = await update.message.photo[-1].get_file()
    save_folder = get_cover_path(update.effective_user.username, update.effective_user.id)
    album_path = f"{save_folder}/{uuid.uuid4()}.png"
    # youtube thumbnails are automatically downloaded. If it is saved, remove the file
    if context.user_data.get('album_path'):
        os.remove(context.user_data['album_path'])
    context.user_data['album_path'] = album_path
    os.makedirs(save_folder, exist_ok=True)

    await photo.download_to_drive(album_path)

    reply_markup = InlineKeyboardMarkup(rpm_keyboard)
    await context.bot.edit_message_text(text='✅Ваше зображення збережено!', chat_id=update.effective_chat.id,  message_id=context.user_data.get('message_id'))
            
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text='Тепер оберіть кількість обертів платівки',
                                    reply_markup=reply_markup)
    context.user_data['message_id'] = message.id        
    
    return RPM
    