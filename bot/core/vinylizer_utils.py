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
        text = 'Ми розпочали вінілізацію вашого відео. Зачекайте трохи'
        if context.user_data.get('message_id'):
            await context.bot.edit_message_text(chat_id=chat_id, text=text, message_id=context.user_data['message_id'])
            
        else:
            await context.bot.send_message(chat_id, text=text)
        result = await loop.run_in_executor(executor, render_video, *args, **kwargs)
        await context.bot.send_video_note(chat_id, result, duration=60)
        text = '''
            Ваше відео готове! Рекомендуємо придбати преміум /premium для кращого користувацького досвіду.
        '''
        await context.bot.send_message(chat_id, text=text)
    except Exception as e:
        logger.error(f"Error rendering video: {traceback.format_exc()}")
        text = 'Сталася помилка під час створення відео.'
        if context.user_data.get('message_id'):
            await context.bot.edit_message_text(chat_id=chat_id, text=text, message_id=context.user_data['message_id'])
            context.user_data['message_id'] = None
        else:
            await context.bot.send_message(chat_id, text=text)