from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from bot.core.vynilize_utils import render_and_send_video
import asyncio

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
    userid = update.effective_user.id
    music_name = context.user_data.get('music_name')
    album = context.user_data.get('album')
    noise = context.user_data.get('noise')
    rpm = context.user_data.get('rpm')


    await context.bot.send_message(update.effective_chat.id, text='Ми розпочали вінілізацію вашого відео. Зачекайте трохи')

    asyncio.create_task(
        render_and_send_video(
            context,
            update.effective_chat.id,
            username,
            userid,
            music_name,
            album, 
            noise, 
            rpm, 
            start_time
        )
    )

    return ConversationHandler.END