from telegram import Update
from telegram.ext import ContextTypes
from bot.config import logger
from .time_state import TIME
from .state_utils import send_time_choice_message

NOISE = 5


async def noise_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the noise decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data
    user = update.effective_user

    message_id = context.user_data.get('message_id')

    if decision == 'Yes':
        context.user_data['noise'] = True
        await context.bot.edit_message_text(text='✅Вініловий шум буде додано до відео!', chat_id=update.effective_chat.id, 
                                message_id=message_id, reply_markup=None)
    else:
        context.user_data['noise'] = False
        await context.bot.edit_message_text(text='❌Вініловий шум НЕ буде додано до відео!', chat_id=update.effective_chat.id,
                                            message_id=message_id, reply_markup=None)

    await send_time_choice_message(update, context, user)

    return TIME
    
    