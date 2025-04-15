from telegram import Update
from telegram.ext import ContextTypes

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = '''
Я - бот-вінілізатор💽. Я можу перетворити вашу пісню на відео-кружечок у вигляді вінілової пластинки♻️.
Бот дозволяє детально налаштувати кожен аспект відео🔧.
Ось список команд:
- /start - запустити бота.
- /help - отримати це повідомлення.
- /vinylize - розпочати процес вінілізації.
'''

    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)