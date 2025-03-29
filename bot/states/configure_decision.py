from telegram import Update, VideoNote, Video
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger
from bot.core import Vynilizer

CONFIGURE_DECISION = 1


async def configure_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the user's decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data

    match decision:
        case 'Continue':
            music_name = context.user_data.get('music_name')
            vynilizer = Vynilizer(update.effective_user, music=music_name)

            await context.bot.send_message(update.effective_chat.id, text='Ми розпочали вінілізацію вашого відео. Зачекайте трохи')

            result = await vynilizer.vynilize()


            await context.bot.send_video_note(update.effective_chat.id, result, duration=59)

            
            
    
    return ConversationHandler.END