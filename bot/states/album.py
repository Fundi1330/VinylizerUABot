from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from .rpm import RPM
from bot.keyboards import rpm_keyboard
from bot.core.utils import get_default_image
from .save_image import SAVE_IMAGE

ALBUM = 2


async def album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the album image decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data


    match decision:
        case 'Default':
            context.user_data['album'] = get_default_image()

            reply_markup = InlineKeyboardMarkup(rpm_keyboard)

            await context.bot.send_message(chat_id=update.effective_chat.id, text='✅Вибрано стандартне зображення!')
            
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Тепер оберіть кількість обертів платівки',
                                            reply_markup=reply_markup)

            return RPM

        case 'Custom':
            await context.bot.send_message(chat_id=update.effective_chat.id, text='🖼️Будь ласка, завантажте зображення')

            return SAVE_IMAGE
            
        case _:
            return ConversationHandler.END
    
    