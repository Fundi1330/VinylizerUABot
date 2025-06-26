from concurrent.futures import ThreadPoolExecutor
from telegram.ext import ContextTypes
from telegram import InputFile
import asyncio
from bot.config import logger
from bot.core.vinylizer import Vinylizer
import traceback

v = Vinylizer()

executor = ThreadPoolExecutor(max_workers=4)

def render_video(*args, **kwargs):
    return v.vinylize(*args, **kwargs)

async def render_and_send_video(context: ContextTypes.DEFAULT_TYPE, chat_id: int, *args, **kwargs):
    loop = asyncio.get_running_loop()
    try:
        await context.bot.send_message(chat_id, text='Ми розпочали вінілізацію вашого відео. Зачекайте трохи')
        result = await loop.run_in_executor(executor, render_video, *args, **kwargs)
        await context.bot.send_video_note(chat_id, result, duration=60)
    except Exception as e:
        logger.error(f"Error rendering video: {traceback.format_exc()}")
        await context.bot.send_message(chat_id, text='Сталася помилка під час створення відео.')