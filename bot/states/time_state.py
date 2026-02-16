from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from .manual_time_choice import MANUAL_TIME_CHOICE
from bot.core.database.utils import get_or_create_user
from .state_utils import send_time_choice_message, create_queue_task

TIME = 6


async def time_state_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the user's start time decision and starts the vinylization process'''
    query = update.callback_query
    await query.answer()
    start_time = None
    user = get_or_create_user(update.effective_user.id)
    if user is None:
        text = '''
            Виникла помилка під час обробки вашого запиту
        '''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return ConversationHandler.END

    if query.data == 'manually' and user.is_premium:
        text = 'Будь ласка, надішліть тайм-код початку пісні'
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, text=text, 
                                            reply_markup=None, message_id=context.user_data.get('message_id'))
        return MANUAL_TIME_CHOICE   
    elif query.data == 'manually' and not user.is_premium:
        text = 'Дана функція доступна лише преміум-користувачам. /premium'
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, text=text, 
                                            reply_markup=None, message_id=context.user_data.get('message_id'))
        return TIME   
    try:
        start_time = int(query.data)
        context.user_data['start_time'] = start_time
    except ValueError:
        logger.error('Start time should be a number')
        return 
    
    await context.bot.edit_message_text(text='✅Час початку обрано!', chat_id=update.effective_chat.id,  message_id=context.user_data.get('message_id'), reply_markup=None)
    context.user_data['message_id'] = None

    await create_queue_task(update, context)

    return ConversationHandler.END