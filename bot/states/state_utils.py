from telegram import Update, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from bot.keyboards import generate_time_keyboard
from bot.config import config
from moviepy import AudioFileClip
from bot.core import get_queue, RenderJob
from bot.keyboards import vinyl_keyboard
from bot.core.utils import get_vinyl_list
from pathlib import Path

async def send_time_choice_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    music = context.user_data.get('music_name')
    music_path = config.get('assets_path') + f'user_audios/{user.username}_{user.id}/{music}'
    audio_length = AudioFileClip(music_path).duration
    
    reply_markup = InlineKeyboardMarkup(generate_time_keyboard(audio_length))

    message = await context.bot.send_message(chat_id=update.effective_chat.id, text='Оберіть час початку звуку!',
                                            reply_markup=reply_markup)
    context.user_data['message_id'] = message.id

async def send_vinyl_choice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
    ☝️☝️☝️
    Який стиль вінілу ви хочете використовувати?
    '''
    reply_markup = InlineKeyboardMarkup(vinyl_keyboard)
    vinyl_list = get_vinyl_list()
    media = []
    for v in vinyl_list:
        with open(Path(config.get('assets_path'), 'default', v['preview_image']), 'rb') as f:
            media.append(InputMediaPhoto(media=f.read()))


    media = await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    context.user_data['message_id'] = message.id
    context.user_data['media'] = media

async def create_queue_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Adds task to the vinylizer queue. Used in advanced vinylization configuration'''
    username = update.effective_user.username
    user_id = update.effective_user.id
    music_name = context.user_data.get('music_name')
    album = context.user_data.get('album')
    noise = context.user_data.get('noise', False)
    rpm = context.user_data.get('rpm', 10)
    start_time = context.user_data.get('start_time', 0)
    vinyl = context.user_data.get('vinyl', 'default')

    queue = get_queue(user_id)

    job = RenderJob(
        context,
        update.effective_chat.id,
        username,
        user_id,
        music_name,
        vinyl,
        False,
        album, 
        noise, 
        rpm, 
        start_time
    )
    await queue.start_worker()
    await queue.add_job_to_queue(job, user_id, update, context)