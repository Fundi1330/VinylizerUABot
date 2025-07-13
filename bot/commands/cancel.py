from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Процес було успішно зупинено!')
    return ConversationHandler.END