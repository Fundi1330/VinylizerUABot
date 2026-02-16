from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .album import ALBUM
from bot.keyboards import image_keyboard
from bot.core.utils import get_vinyl_list
from .state_utils import send_vinyl_choice_message
from bot.core import session
from bot.core import User as UserModel
from bot.config import logger

SELECT_VINYL = 8 

async def select_vinyl_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Saves the user vinyl'''
    await update.callback_query.answer()
    vinyl_ind = update.callback_query.data
    vinyl_list = get_vinyl_list()
    vinyl = vinyl_list[int(vinyl_ind)]
    user = session.query(UserModel).filter_by(telegram_id=update.effective_user.id).first()

    if vinyl['is_premium'] and not user.is_premium:
        text = '''❌Даний стиль вінілу доступний лише преміум-користувачам /premium.
        Оберіть інший'''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        await send_vinyl_choice_message(update, context)
        return SELECT_VINYL
    context.user_data['vinyl'] = vinyl['name']

    text = '''
    ✅Стиль вінілу успішно обрано!
    '''

    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=context.user_data.get('message_id'),
                                        text=text)

    text = '''
    Яке зображення ви хочете використовувати?
    '''
    reply_markup = InlineKeyboardMarkup(image_keyboard)

    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    context.user_data['message_id'] = message.id

    return ALBUM