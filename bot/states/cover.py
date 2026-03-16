from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from .rpm import RPM
from bot.keyboards import rpm_keyboard
from bot.core.utils import get_default_image
from .save_image import SAVE_IMAGE

COVER = 2


async def cover_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the cover image decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data


    match decision:
        case 'Default':
            reply_markup = InlineKeyboardMarkup(rpm_keyboard)
            await context.bot.edit_message_text(text='✅Вибрано стандартне зображення!', chat_id=update.effective_chat.id,  message_id=context.user_data.get('message_id'), reply_markup=None)
            
            message = await context.bot.send_message(chat_id=update.effective_chat.id, text='Тепер оберіть кількість обертів платівки',
                                            reply_markup=reply_markup)
            context.user_data['message_id'] = message.id

            return RPM

        case 'Custom':
            await context.bot.edit_message_text(text='🖼️Будь ласка, завантажте зображення', chat_id=update.effective_chat.id,  message_id=context.user_data.get('message_id'), reply_markup=None)

            return SAVE_IMAGE
            
        case _:
            return ConversationHandler.END
    
    