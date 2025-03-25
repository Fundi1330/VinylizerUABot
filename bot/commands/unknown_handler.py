from telegram import Update
from telegram.ext import ContextTypes

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Пробачте, я не зміг розпізнати команду! Скоріш за все її не існує')