from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from bot.core import Vynilizer

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

    music_name = context.user_data.get('music_name')
    album = context.user_data.get('album')
    noise = context.user_data.get('noise')
    rpm = context.user_data.get('rpm')

    vynilizer = Vynilizer(update.effective_user, music=music_name)


    await context.bot.send_message(update.effective_chat.id, text='Ми розпочали вінілізацію вашого відео. Зачекайте трохи')

    result = await vynilizer.vynilize(album_cover=album, add_vinyl_noise=noise, rpm=rpm, start=start_time)
    await context.bot.send_video_note(update.effective_chat.id, result, duration=59)

    return ConversationHandler.END