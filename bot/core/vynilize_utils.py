from concurrent.futures import ThreadPoolExecutor
from telegram.ext import ContextTypes
import asyncio
from bot.config import logger
from .vinylize import Vynilizer

executor = ThreadPoolExecutor(max_workers=4)

def render_video(username: str, userid: int, music: str, *args, **kwargs):
    vynilizer = Vynilizer(username, userid, music)
    return vynilizer.vynilize(*args, **kwargs)

async def render_and_send_video(context: ContextTypes.DEFAULT_TYPE, chat_id: int, username: str, userid: int, music_name: str, *args):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(executor, render_video, username, userid, music_name, *args)
        await context.bot.send_video_note(chat_id, result, duration=60)
    except Exception as e:
        logger.error(f"Error rendering video: {e}")
        await context.bot.send_message(chat_id, text='Сталася помилка під час створення відео.')