from telegram import Update, InlineKeyboardMarkup, Audio, User, Video
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest
from bot.core.database.utils import get_or_create_user
from bot.keyboards import configure_keyboard
from .decision import CONFIGURE_DECISION
from bot.config import config, logger
import os
import subprocess
import uuid
from movielite import AudioClip
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bot.core.utils import get_user_audio_path, get_cover_path, save_audio_cover, get_max_duration
from pathlib import Path
import yt_dlp
from babel.dates import format_timedelta
import datetime

CONFIGURE = 0

executor = ThreadPoolExecutor(max_workers=4)

class AllowedVideoDurationExceededError(Exception):
    pass

def run_save_audio_process(cmd_args: list, context: ContextTypes.DEFAULT_TYPE, save_path: str):
    subprocess.run(cmd_args, check=True)
    audio = AudioClip(save_path)
    context.user_data['audio_path'] = save_path
    context.user_data['audio_duration'] = audio.duration

async def download_audio(audio: Audio, context: ContextTypes.DEFAULT_TYPE, audio_path: str, cover_path: str, max_duration: int) -> None:
    if audio.duration > max_duration:
        raise AllowedVideoDurationExceededError()
    
    file_id = audio.file_id
    file = await context.bot.get_file(file_id)
    await file.download_to_drive(audio_path)
    context.user_data['audio_path'] = audio_path
    cover = save_audio_cover(audio_path, cover_path)
    if cover:
        context.user_data['cover_path'] = cover

async def download_video(video: Video, context: ContextTypes.DEFAULT_TYPE, audio_folder: str, max_duration: int) -> None:
    if video.duration > max_duration:
        raise AllowedVideoDurationExceededError()
    file_id = video.file_id
    file = await context.bot.get_file(file_id)

    video_path = await file.download_to_drive(str(Path(audio_folder) / video.file_name))
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
        os.remove(video_path)
    except subprocess.CalledProcessError as e:
        logger.error(f'An error occured while converting the video to audio: {e}')
        raise

async def download_audio_from_youtube(link: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE, audio_folder: str, cover_folder: str, max_duration: int) -> None:
    # Check video duration before downloading
    def get_video_duration():
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('duration', 0)
    
    try:
        loop = asyncio.get_running_loop()
        video_duration = await loop.run_in_executor(executor, get_video_duration)
        
        if video_duration > max_duration:
            raise AllowedVideoDurationExceededError()
    except Exception as e:
        logger.error(f'An error occurred while checking video duration: {e}')
        raise e
    
    audio_id = str(uuid.uuid4())
    audio_output_template = str(Path(audio_folder, audio_id))
    cover_output_template = str(Path(cover_folder, audio_id))
    audio_path = f'{audio_output_template}.mp3'
    cover_path = f'{cover_output_template}.webp'

    def download_audio_task():
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': audio_output_template,
            'quiet': False,
            'no_warnings': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(link, download=True)
    
    def download_thumbnail_task():
        ydl_opts = {
            'writethumbnail': True,
            'skip_download': True,
            'outtmpl': cover_output_template,
            'quiet': False,
            'no_warnings': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(link, download=True)
    
    try:
        loop = asyncio.get_running_loop()
        
        # Run both tasks in parallel
        await asyncio.gather(
            loop.run_in_executor(executor, download_audio_task),
            loop.run_in_executor(executor, download_thumbnail_task)
        )
        audio = AudioClip(audio_path)
        context.user_data['audio_path'] = audio_path
        context.user_data['audio_duration'] = audio.duration
        context.user_data['cover_path'] = cover_path
    except Exception as e:
        logger.error(f'An error occurred while downloading from YouTube: {e}')
        edited_text = '''
            Під час завантаження відео виникла помилка!
        '''
        await context.bot.send_message(chat_id=chat_id, text=edited_text)
    

async def file_download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Downloads audio and asks user what he wants to do next'''
    user = get_or_create_user(update.effective_user.id)

    max_duration = get_max_duration(user.is_premium)
    chat_id = update.effective_chat.id

    audio_folder = get_user_audio_path(update.effective_user.username, update.effective_user.id)
    cover_folder = get_cover_path(update.effective_user.username, update.effective_user.id)
    audio_name = f"{uuid.uuid4()}.mp3"
    audio_path = str(Path(audio_folder, audio_name))
    cover_name = f'{uuid.uuid4()}.png'
    cover_path = str(Path(cover_folder, cover_name))

    try:
        if update.message.audio:
            await download_audio(update.message.audio, context, audio_path, cover_path, max_duration)

        elif update.message.video and user.is_premium:
            video = update.message.video
            text = '''
                🔃Відео завантажується...
            '''
            message = await context.bot.send_message(chat_id=chat_id, text=text)
            await download_video(video, context, audio_folder, max_duration)
            text = '''
                📩Відео успішно завантажено!
            '''
            await message.edit_text(text=text)

        elif update.message.text and user.is_premium:
            text = '''
                🔃Відео завантажується...
            '''
            message = await context.bot.send_message(chat_id=chat_id, text=text)
            await download_audio_from_youtube(update.message.text, chat_id, context, audio_folder, cover_folder, max_duration)
            text = '''
                📩Ютуб-Відео успішно завантажено!
            '''
            await message.edit_text(text=text)
        elif (update.message.video and not user.is_premium) or (update.message.text and not user.is_premium):
            text = '''
                Дана функція доступна лише преміум-користувачам.
                \n/premium
            '''
            await context.bot.send_message(chat_id=chat_id, text=text)
            return ConversationHandler.END
    except AllowedVideoDurationExceededError:
        time_left = datetime.timedelta(seconds=max_duration)
        text = f'''
            ❌Довживна занадто велика. Ваш аккаунт дозволяє завантажувати максимальною довжиною в {
                format_timedelta(time_left, format="short", locale="uk_UA")
            }
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)
        return ConversationHandler.END
    except BadRequest:
        text = '''
            ❌Розмір файлу занадто великий. Спробуйте зменшити його розмір, або ви можете придбати преміум та завантажити його на ютуб
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)
        return ConversationHandler.END
    except subprocess.CalledProcessError:
        text = '''
            ❌Під час завантаження відео виникла помилка!
        '''
        await context.bot.send_message(chat_id=chat_id, text=text)
        return ConversationHandler.END
    

    text = '''
    Оберіть, що ви хочете робити далі👇.
    '''
    reply_markup = InlineKeyboardMarkup(configure_keyboard)

    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    context.user_data['message_id'] = message.id

    return CONFIGURE_DECISION