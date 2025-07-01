from telegram import Update
from telegram.ext import ContextTypes
from bot.config import config
from bot.core import User, session

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Confirms the payment details'''
    query = update.pre_checkout_query
    user = session.query(User).filter_by(telegram_id=update.effective_user.id).one_or_none()
    

    if query.invoice_payload != config.get('payload') or user is None:
        await query.answer(ok=False, error_message='Виникла помилка під час обробки вашої оплати...')
    elif user.is_premium:
        await query.answer(ok=False, error_message='Ви уже маєте преміум')
    else:
        plans: dict = config.get('plans', None)
        for plan in plans:
            if plan['price'] == query.total_amount:
                context.user_data['plan_duration'] = plan['length']
        await query.answer(ok=True)
    