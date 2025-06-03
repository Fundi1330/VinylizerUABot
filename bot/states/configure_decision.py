from telegram import Update, InlineKeyboardMarkup
from bot.keyboards import image_keyboard
from telegram.ext import ContextTypes, ConversationHandler
from bot.core.vynilize_utils import render_and_send_video
from .album import ALBUM
import asyncio

CONFIGURE_DECISION = 1

async def configure_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the user's decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data

    music_name = context.user_data.get('music_name')
    username = update.effective_user.username
    userid = update.effective_user.id

    match decision:
        case 'Continue':
            await context.bot.send_message(update.effective_chat.id, text='Ми розпочали вінілізацію вашого відео. Зачекайте трохи')
            
            asyncio.create_task(
                render_and_send_video(
                    context,
                    update.effective_chat.id,
                    username,
                    userid,
                    music_name
                )
            )
            return ConversationHandler.END
        case 'Configure':
            text = '''
            Яке зображення ви хочете використовувати?
            '''
            reply_markup = InlineKeyboardMarkup(image_keyboard)

            await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
            
            return ALBUM
        case _:
            return ConversationHandler.END
    
    