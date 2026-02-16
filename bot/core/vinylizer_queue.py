from telegram.ext import ContextTypes
from telegram import Update
import asyncio
from bot.core.vinylizer_utils import render_and_send_video
from bot.core.database.utils import get_or_create_user
from bot.config import logger

class RenderJob:
    def __init__(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, username: str, user_id: int, music_name: str, *args, **kwargs):
        self.context = context
        self.chat_id = chat_id
        self.user = {
            'username': username,
            'id': user_id
        }
        self.music_name = music_name
        self.args = args
        self.kwargs = kwargs

class VinylizerQueue(asyncio.Queue):
    def __init__(self, maxsize = 0):
        self.locks = dict()
        self.task_amount = 0
        self.__running = False
        super().__init__(maxsize)

    async def start_worker(self):
        if not self.__running:
            logger.info("Starting queue worker...")
            self.__running = True
            asyncio.create_task(
                self.__worker()
            )

    async def stop_worker(self):
        self.__running = False
        await self.join()

    async def __worker(self):
        while self.__running:
            job: RenderJob = await self.get()

            user_id = job.user.get('id')
            lock: asyncio.Lock = self.get_lock_by_user_id(user_id)
            await render_and_send_video(
                job.context,
                job.chat_id,
                job.user.get('username'),
                job.user.get('id'),
                job.music_name,
                *job.args,
                **job.kwargs
            )
            if lock.locked():
                lock.release()
            self.task_amount -= 1

        self.task_done()
        
    
    def get_lock_by_user_id(self, user_id: int):
        lock: asyncio.Lock | None = self.locks.get(user_id)
        if not lock: 
            self.locks[user_id] = lock = asyncio.Lock()
        return lock

    def get_size(self):
        return self.task_amount
    
    async def add_job_to_queue(self, job: RenderJob, user_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        lock = self.get_lock_by_user_id(user_id)
        size = self.get_size()
        user = get_or_create_user(user_id)

        
        if lock.locked() and not user.is_premium:
            text = get_locked_message(size)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        else:
            if not lock.locked():
                await lock.acquire()
            if size > 0:
                text = f'Вас було додано до черги. Перед вами ще {size} користувачів. Зачекайте трохи!'
                message = await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                context.user_data['message_id'] = message.id
            
            await self.put(job)
            self.task_amount += 1
    
def get_locked_message(size: int):
    message = f'Ви уже створили пластинку. Щоб рендерити кілька пластинок одночасно ви можете придбати преміум - /premium.'
    if size > 0:
        message += f'\nПеред вами ще {size} людей'
    return message