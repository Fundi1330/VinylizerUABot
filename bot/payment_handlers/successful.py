from telegram import Update
from telegram.ext import ContextTypes
from bot.core import Premium, User, session
import datetime
from dateutil.relativedelta import relativedelta

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
        Дякуємо за покупку! Щасливого вам використання преміуму!
    '''
    user = session.query(User).filter_by(telegram_id=update.effective_user.id).one_or_none()
    if user is None:
        text = '''
            Сталася помилка під час обробки вашого замовлення
        '''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    

    premium = user.premium
    if premium is None:
        expire_date = datetime.datetime.now() + relativedelta(months=context.user_data['plan_duration'])
        premium = Premium(user_id=user.id, expire_date=expire_date)
        premium.user = user
        session.add(premium)
        session.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)