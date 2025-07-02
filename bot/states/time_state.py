from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from bot.core.vinylizer_queue import RenderJob
from bot.core import get_queue

TIME = 6


async def time_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the user's decision'''
    query = update.callback_query
    await query.answer()
    start_time = None
    try:
        start_time = int(query.data)
    except ValueError:
        logger.error('Start time should be a number')
        return 

    username = update.effective_user.username
    user_id = update.effective_user.id
    music_name = context.user_data.get('music_name')
    album = context.user_data.get('album')
    noise = context.user_data.get('noise')
    rpm = context.user_data.get('rpm')

    queue = get_queue(user_id)

    job = RenderJob(
        context,
        update.effective_chat.id,
        username,
        user_id,
        music_name,
        False,
        album, 
        noise, 
        rpm, 
        start_time
    )
    await queue.start_worker()
    await queue.add_job_to_queue(job, user_id, update, context)

    return ConversationHandler.END