from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes
from bot.keyboards import generate_premium_invoice_keyboard
from bot.config import config

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
        Преміум є щомісячною підпискою, яка дозволяє вам:
        \n- Рендерити відео в окремій черзі для преміум-користувачів.
        \n- Додавати кілька відео до черги.
    '''
    premium_keyboard = await generate_premium_invoice_keyboard(context.bot)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=premium_keyboard)