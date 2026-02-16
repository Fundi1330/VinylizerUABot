from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.core import get_queue
from .select_vinyl import SELECT_VINYL
from .state_utils import send_vinyl_choice_message
from bot.config import logger
from bot.core.vinylizer_queue import RenderJob

CONFIGURE_DECISION = 1

async def decision_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the user's decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data

    music_name = context.user_data.get('music_name')
    username = update.effective_user.username
    user_id = update.effective_user.id

    queue = get_queue(user_id)

    match decision:
        case 'Continue':
            job = RenderJob(
                context,
                update.effective_chat.id,
                username,
                user_id,
                music_name,
                False
            )
            await queue.start_worker()
            await queue.add_job_to_queue(job, user_id, update, context)
            
            return ConversationHandler.END
        case 'Configure':
            await send_vinyl_choice_message(update, context)
            return SELECT_VINYL
        case _:
            return ConversationHandler.END
    
    