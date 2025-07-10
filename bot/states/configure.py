from telegram import Update, InlineKeyboardMarkup, Audio, User
from telegram.ext import ContextTypes, ConversationHandler
from bot.core.database import User as UserModel
from bot.core.database import session
from bot.keyboards import configure_keyboard
from .configure_decision import CONFIGURE_DECISION
from bot.config import config, logger
from os import makedirs
import os
import subprocess
import uuid

CONFIGURE = 0

async def download_audio(audio: Audio, context: ContextTypes.DEFAULT_TYPE, user: User):
    context.user_data['music_name'] = audio.file_name

    file_id = audio.file_id
    new_file = await context.bot.get_file(file_id)
    save_folder = f'bot/assets/user_audios/{user.username}_{user.id}/'
    makedirs(save_folder, exist_ok=True)

    await new_file.download_to_drive(f'{save_folder}/{audio.file_name}')

async def download_video(video: Audio, chat_id: int, context: ContextTypes.DEFAULT_TYPE, user: User):
    file_id = video.file_id
    new_file = await context.bot.get_file(file_id)
    save_folder = f'bot/assets/user_audios/{user.username}_{user.id}/'
    makedirs(save_folder, exist_ok=True)

    video_path = await new_file.download_to_drive(f'{save_folder}/{video.file_name}')
    audio_name = f'{video.file_name.split('.')[0]}.mp3'
    audio_path = f'{save_folder}/{audio_name}'
    context.user_data['music_name'] = audio_name
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vn',
        '-acodec', 'libmp3lame',
        '-ab', '192k',
        '-ar', '44100',
        '-y',
        audio_path

    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        text = '''
            📩Відео успішно завантажено!
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)
        os.remove(video_path)
    except subprocess.CalledProcessError as e:
        logger.error(f'An error occured while converting the video to audio: {e}')
        text = '''
            Під час завантаження відео виникла помилка!
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)

async def download_audio_from_youtube(link: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE, user: User):
    text = '''
        🔃Відео завантажується...
    '''
    message = await context.bot.send_message(chat_id=chat_id, text=text)
    audio_name = f'{uuid.uuid4()}.mp3'
    context.user_data['music_name'] = audio_name
    save_folder = f'bot/assets/user_audios/{user.username}_{user.id}/'
    makedirs(save_folder, exist_ok=True)
    ytdlp_cmd = [
        'yt-dlp',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--output', f'{save_folder}/{audio_name}',
        link
    ]

    try:
        subprocess.run(ytdlp_cmd, check=True)
        edited_text = '''
            📩Ютуб-відео успішно завантажено!
        '''
    except subprocess.CalledProcessError as e:
        logger.error(f'An error occured while extracting audio from youtube video: {e}')
        edited_text = '''
            Під час завантаження відео виникла помилка!
        '''
    finally:
        await context.bot.edit_message_text(chat_id=chat_id, text=edited_text, message_id=message.message_id)
    



async def configure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Downloads music and asks user what he wants to do next'''
    user = session.query(UserModel).filter_by(telegram_id=update.effective_user.id).one_or_none()
    if user is None:
        text = '''
            Виникла помилка під час обробки вашого запиту
        '''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return ConversationHandler.END
    if update.message.audio:
        await download_audio(update.message.audio, context, update.effective_user)
    elif update.message.video and user.is_premium:
        await download_video(update.message.video, update.effective_chat.id, context, update.effective_user)
    elif update.message.text and user.is_premium:
        logger.info(update.message.text)
        await download_audio_from_youtube(update.message.text, update.effective_chat.id, context, update.effective_user)
    else:
        text = '''
            Дана функція доступна лише преміум-користувачам.
            \n/premium
        '''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return ConversationHandler.END

    

    text = '''
    Оберіть, що ви хочете робити далі👇.
    '''
    reply_markup = InlineKeyboardMarkup(configure_keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return CONFIGURE_DECISION