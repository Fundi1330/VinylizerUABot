from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message('Процес було успішно зупинено!')
    return ConversationHandler.END