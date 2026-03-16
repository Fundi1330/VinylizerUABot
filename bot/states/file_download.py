from telegram import Update, InlineKeyboardMarkup, Audio, User
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest
from bot.core.database.utils import get_or_create_user
from bot.keyboards import configure_keyboard
from .decision import CONFIGURE_DECISION
from bot.config import config, logger
from os import makedirs
import os
import subprocess
import uuid
from movielite import AudioClip
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bot.core.utils import get_user_audio_path, get_cover_path, save_audio_cover
from functools import partial
from pathlib import Path

CONFIGURE = 0

executor = ThreadPoolExecutor(max_workers=4)

def run_save_audio_process(cmd_args: list, context: ContextTypes.DEFAULT_TYPE, save_path: str):
    subprocess.run(cmd_args, check=True)
    audio = AudioClip(save_path)
    context.user_data['audio_path'] = save_path
    context.user_data['audio_duration'] = audio.duration

async def download_audio(audio: Audio, chat_id: int, context: ContextTypes.DEFAULT_TYPE, user: User) -> int:
    file_id = audio.file_id
    try:
        new_file = await context.bot.get_file(file_id)
    except BadRequest as e:
        text = '''
            ❌Розмір аудіо занадто великий. Спробуйте зменшити його розмір
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)
        return -1
    audio_folder = get_user_audio_path(user.username, user.id)
    makedirs(audio_folder, exist_ok=True)

    audio_name = f"{uuid.uuid4()}.mp3"
    audio_path = str(Path(audio_folder) / audio_name)
    await new_file.download_to_drive(audio_path)
    context.user_data['audio_path'] = audio_path
    cover_name = f'{uuid.uuid4()}.png'
    cover_path = str(Path(get_cover_path(user.username, user.id), cover_name))
    cover = save_audio_cover(audio_path, cover_path)
    if cover:
        context.user_data['cover_path'] = cover
    return 0

async def download_video(video: Audio, chat_id: int, context: ContextTypes.DEFAULT_TYPE, user: User) -> int:
    text = '''
        🔃Відео завантажується...
    '''
    message = await context.bot.send_message(chat_id=chat_id, text=text)
    file_id = video.file_id
    try:
        new_file = await context.bot.get_file(file_id)
    except BadRequest as e:
        text = '''
            ❌Розмір відео занадто великий. Спробуйте зменшити його розмір, або ви можете завантажити його на ютуб
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)
        return -1
    audio_folder = get_user_audio_path(user.username, user.id)
    makedirs(audio_folder, exist_ok=True)

    video_path = await new_file.download_to_drive(str(Path(audio_folder) / video.file_name))
    audio_name = f'{uuid.uuid4()}.mp3'
    save_path = str(Path(audio_folder) / audio_name)
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vn',
        '-acodec', 'libmp3lame',
        '-ab', '192k',
        '-ar', '44100',
        '-y',
        save_path
    ]

    try:
        await asyncio.get_running_loop().run_in_executor(
            executor, run_save_audio_process, ffmpeg_cmd, context, save_path
        )
        text = '''
            📩Відео успішно завантажено!
        '''
        await message.edit_text(text=text)
        os.remove(video_path)
    except subprocess.CalledProcessError as e:
        logger.error(f'An error occured while converting the video to audio: {e}')
        text = '''
            Під час завантаження відео виникла помилка!
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)
        return -1
    return 0

async def download_audio_from_youtube(link: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE, user: User) -> int:
    text = '''
        🔃Відео завантажується...
    '''
    message = await context.bot.send_message(chat_id=chat_id, text=text)
    audio_name = f'{uuid.uuid4()}'
    
    audio_folder = get_user_audio_path(user.username, user.id)
    makedirs(audio_folder, exist_ok=True)
    audio_save_path = str(Path(audio_folder) / audio_name)
    ytdlp_audio_cmd = [
        'yt-dlp',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--output', audio_save_path,
        link
    ]
    cover_folder = get_cover_path(user.username, user.id)
    cover_save_path = str(Path(f"{str(Path(cover_folder) / audio_name)}"))
    ytdlp_thumbnail_cmd = [
        'yt-dlp',
        '--write-thumbnail',
        '--skip-download',
        '--output', cover_save_path,
        link
    ]

    try:
        await asyncio.gather(
            asyncio.get_running_loop().run_in_executor(
                executor, 
                run_save_audio_process, 
                ytdlp_audio_cmd, 
                context, 
                f'{audio_save_path}.mp3'
            ),
            asyncio.get_running_loop().run_in_executor(
                executor, 
                partial(
                    subprocess.run, 
                    ytdlp_thumbnail_cmd, 
                    check=True
                )
            )
        )
        
        context.user_data['cover_path'] = f'{cover_save_path}.webp'
        edited_text = '''
            📩Ютуб-відео успішно завантажено!
        '''
        await message.edit_text(text=edited_text)
        
    except subprocess.CalledProcessError as e:
        logger.error(f'An error occured while extracting audio from youtube video: {e}')
        edited_text = '''
            Під час завантаження відео виникла помилка!
        '''
        await context.bot.send_message(chat_id=chat_id, text=edited_text)
        return -1
    return 0
    

async def file_download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Downloads audio and asks user what he wants to do next'''
    user = get_or_create_user(update.effective_user.id)

    result = None
    if update.message.audio:
        result = await download_audio(update.message.audio, update.effective_chat.id, context, update.effective_user)
    elif update.message.video and user.is_premium:
        result = await download_video(update.message.video, update.effective_chat.id, context, update.effective_user)
    elif update.message.text and user.is_premium:
        result = await download_audio_from_youtube(update.message.text, update.effective_chat.id, context, update.effective_user)
    else:
        text = '''
            Дана функція доступна лише преміум-користувачам.
            \n/premium
        '''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return ConversationHandler.END
    if result is not None and result == -1:
        return ConversationHandler.END
    

    text = '''
    Оберіть, що ви хочете робити далі👇.
    '''
    reply_markup = InlineKeyboardMarkup(configure_keyboard)

    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    context.user_data['message_id'] = message.id

    return CONFIGURE_DECISION