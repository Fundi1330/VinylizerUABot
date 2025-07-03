from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.states import CONFIGURE
from bot.core import get_queue, get_locked_message
from bot.core.database import session, User
from bot.config import logger

async def vinylize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    queue = get_queue(update.effective_user.id)
    lock = queue.get_lock_by_user_id(update.effective_user.id)
    size = queue.get_size()
    user = session.query(User).filter_by(telegram_id=update.effective_user.id).one_or_none()
    
    if lock.locked() and not user.is_premium:
        message = get_locked_message(size)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return ConversationHandler.END
    text = '''
    Надішліть аудіо, відео або посилання на ютуб-відео
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return CONFIGURE