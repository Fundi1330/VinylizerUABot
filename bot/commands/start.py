from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
    Вітаю👋! Я - бот-вінілізатор.
    Надішліть мені аудіо і я перетворю його у кружечок з вініловою пластинкою.
    Напишіть /vinylize, щоб розпочати.
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)