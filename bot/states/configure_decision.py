from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.config import logger

CONFIGURE_DECISION = 1


async def configure_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Handles the result of the user's decision'''
    query = update.callback_query
    await query.answer()
    decision = query.data

    match decision:
        case 'Continue':
            await context.bot.send_message(update.effective_chat.id, text='Ми розпочали вінілізацію вашого відео. Зачекайте трохи')
            
    
    return ConversationHandler.END