from telegram import Update
from telegram.ext import ContextTypes
from bot.states import CONFIGURE

async def vinylize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
    Надішліть аудіофайл
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return CONFIGURE