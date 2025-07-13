from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from bot.keyboards import yes_no_keyboard
from .noise import NOISE

RPM = 3


async def rpm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the user's rpm choice'''
    query = update.callback_query
    await query.answer()
    rotations = None
    try:
        rotations = int(query.data)
    except ValueError:
        logger.error('Rotations per minute should be a number')
        return 

    context.user_data['rpm'] = rotations

    reply_markup = InlineKeyboardMarkup(yes_no_keyboard)
    
    await context.bot.edit_message_text(text='✅Швидкість обертання обрано!', chat_id=update.effective_chat.id,  message_id=context.user_data.get('message_id'),
                                        reply_markup=None)
    
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text='Чи потрібно додавати вініловий шум?',
                                            reply_markup=reply_markup)
    context.user_data['message_id'] = message.id
            

    return NOISE