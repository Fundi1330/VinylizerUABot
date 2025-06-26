from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.states import CONFIGURE
from bot.core import q, get_locked_message

async def vinylize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lock = q.get_lock_by_user_id(update.effective_user.id)
    size = q.get_size()
    if lock.locked():
        message = get_locked_message(size)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return ConversationHandler.END
    text = '''
    Надішліть аудіофайл
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return CONFIGURE