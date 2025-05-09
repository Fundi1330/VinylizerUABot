from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger, config
from .time_state import TIME
from moviepy import AudioFileClip
from bot.keyboards import generate_time_keyboard

NOISE = 5


async def noise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the album image decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data
    user = update.effective_user

    if decision == 'Yes':
        context.user_data['noise'] = True
        await context.bot.send_message(chat_id=update.effective_chat.id, text='✅Вініловий шум буде додано до відео!' )
    else:
        context.user_data['noise'] = False
        await context.bot.send_message(chat_id=update.effective_chat.id, text='❌Вініловий шум НЕ буде додано до відео!' )

    music = context.user_data.get('music_name')
    music_path = config.get('assets_path') + f'user_audios/{user.username}_{user.id}/{music}'
    audio_length = AudioFileClip(music_path).duration
    
    reply_markup = InlineKeyboardMarkup(generate_time_keyboard(audio_length))

    

    await context.bot.send_message(chat_id=update.effective_chat.id, text='Оберіть час початку звуку!',
                                            reply_markup=reply_markup)
    

    return TIME
    
    