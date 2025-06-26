from telegram.ext import ContextTypes
from telegram import Update
import asyncio
from bot.core.vinylizer_utils import render_and_send_video
from concurrent.futures import ThreadPoolExecutor
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
        self.__running = False
        super().__init__(maxsize)

    async def start_worker(self):
        if not self.__running:
            self.__running = True
            asyncio.create_task(self.__worker())

    async def stop_worker(self):
        self.__running = False
        await self.join()

    async def __worker(self):
        while self.__running:
            job: RenderJob = await self.get()

            user_id = job.user.get('id')
            lock: asyncio.Lock = self.locks.get(user_id, asyncio.Lock())
            
            await render_and_send_video(
                job.context,
                job.chat_id,
                job.user.get('username'),
                job.user.get('id'),
                job.music_name,
                *job.args,
                **job.kwargs
            )
            lock.release()

        self.task_done()
        
    
    def get_lock_by_user_id(self, user_id: int):
        lock: asyncio.Lock | None = self.locks.get(user_id)
        if not lock: 
            self.locks[user_id] = lock = asyncio.Lock()
        return lock

    def get_size(self):
        return len([i for i in self.locks.values() if i.locked()]) - 1
    
    async def add_job_to_queue(self, job: RenderJob, user_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        lock = self.get_lock_by_user_id(user_id)
        size = self.qsize() - 1

        
        if lock.locked():
            message = get_locked_message(size)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            await lock.acquire()

            size = self.get_size()
            
            if size > 0:
                message = f'Вас було додано до черги. Перед вами ще {size} користувачів. Зачекайте трохи!'
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            
            await self.put(job)
    
def get_locked_message(size: int):
    message = f'Ви уже створили пластинку. Щоб рендерити кілька пластинок одночасно ви можете придбати преміум - /premium.'
    if size > 0:
        message += f'Перед вами ще {size} людей'
    return message